import subprocess
import requests
from random import randrange as random_from_range
from time import sleep
from datetime import datetime
import platform
 

class Types:
    connectionstate = "connectionstate"
    debuglogging = "debuglogging"
    portforward = "portforward"
    region = "region"
    requestportforward = "requestportforward"
    protocol = "protocol"
    regions = "regions"
    vpnip = "vpnip"

    class ConnectionStates:
        Disconnected = "Disconnected"
        Connecting = "Connecting"
        StillConnecting = "StillConnecting"
        Connected = "Connected"
        Interrupted = "Interrupted"
        Reconnecting = "Reconnecting"
        StillReconnecting = "StillReconnecting"
        DisconnectingToReconnect = "DisconnectingToReconnect"
        Disconnecting = "Disconnecting"

    class State_Indicators:
        Inactive = "Inactive"
        Attempting = "Attempting"
        Failed = "Failed"
        Unavailable = "Unavailable"



if platform.system() == 'Windows':
    piactl_path = "C:\Program Files\Private Internet Access\piactl.exe"
else:
    piactl_path = "piactl"

options = {
    '--timeout':30,
    '--debug': False, # -d Prints debug logs to stderr.
    '--help': False, # -h
    'version': False
}

class VPNController:
    def __init__(self, piactl_path=piactl_path, timeout=5):
        self.piactl_path = piactl_path
        self.regions = self.get_us_regions()
        self.timeout = timeout
        pass

    def help(self):
        subprocess.run(["piactl", "--help"], check=True)
    def debug(self):
        subprocess.run(["piactl", "--debug"], check=True)
    def version(self):
        subprocess.run(["piactl", "--version"], check=True)

    # Allow the killswitch and/or VPN connection to remain active in the background when the GUI client is not running.
    def enable_background(self):
        subprocess.run(["piactl", "background", "enable"], check=True)
    def disable_background(self):
        subprocess.run(["piactl", "background", "disable"], check=True)
    # Causes PIA to connect to the VPN, if it isn't already connected.
    def connect(self):
        subprocess.run(["piactl", "connect"], check=True)
        start_time = datetime.now()
        while  True:
            if self.get_connectionstate() == 'Connected':
                break
            current_time = datetime.now()
            elapsed_seconds = (current_time - start_time).total_seconds()
            if elapsed_seconds >= self.timeout:
                print(f"Could not connect {self.get_connectionstate()}")
                raise TimeoutError
    #Causes PIA to disconnect from the VPN, if it is connected.
    def disconnect(self):
        subprocess.run(["piactl", "disconnect"], check=True)
        start_time = datetime.now()
        while  True:
            if self.get_connectionstate() == 'Disconnected':
                break
            current_time = datetime.now()
            elapsed_seconds = (current_time - start_time).total_seconds()
            if elapsed_seconds >= self.timeout:
                print(f"Could not disconnect {self.get_connectionstate()}")
                raise TimeoutError
    #Get's connection status of PIA from the VPN.
    def get_connectionstate(self):
        result = subprocess.run(["piactl", "get", "connectionstate"],  capture_output=True, text=True)
        return_code = result.returncode
        output = result.stdout.strip()
        return output
    #
    def get_regions(self):
        result = subprocess.run(["piactl", "get", "regions"],  capture_output=True, text=True)
        return_code = result.returncode
        output = result.stdout.strip()
        return output
    #The current selected region
    def get_region(self):
        result = subprocess.run(["piactl", "get", "region"],  capture_output=True, text=True)
        return_code = result.returncode
        output = result.stdout.strip()
        return output
    def set_region(self,region_name):
        subprocess.run(["piactl", "set", "region",region_name], check=True)
        
        start_time = datetime.now()
        while  True:
            if self.get_connectionstate() == 'Connected':
                break
            current_time = datetime.now()
            elapsed_seconds = (current_time - start_time).total_seconds()
            if elapsed_seconds >= self.timeout:
                print(f"Could not Connect after setting region {self.get_connectionstate()}")
                raise TimeoutError

        return self.get_region()
    

    ##
    # My Functions
    ##
    def start_vpn(self):
        if self.get_connectionstate() != 'Connected':
            self.enable_background()
            self.connect()

        current_region = self.auto_set_region()

        return self.get_connectionstate(), current_region
            
    def auto_set_region(self):
        # Refresh if list depleated
        if not self.regions:
            self.regions = self.get_us_regions()
        # Pick from list
        region=self.regions[random_from_range(len(self.regions))]
        # Remove pick from list
        self.regions.pop(self.regions.index(region))
        current_region = self.set_region(region_name=region)
    
        return current_region

    def get_us_regions(self):
        all_regions = self.get_regions()
        all_regions_list = all_regions.split("\n")
        us_regions = [item for item in all_regions_list if "us-" in item]
        return us_regions
    
    def stop_vpn(self):
        self.disconnect()
        self.disable_background()
        disconnecting = True
        while disconnecting:
            if 'Disconnected' in self.get_connectionstate():
                return self.get_connectionstate()
    
    def get_non_pia_ip(self):
        # Capture Current Connection State
        connection_state = self.get_connectionstate()

        # Disconnect if not already disconnected
        if connection_state != 'Disconnected':
            self.stop_vpn()

        # Capture non API IP
        response = requests.get("https://api.ipify.org")

        # Reconnect if PIA was connected
        if connection_state == 'Connected':
            self.start_vpn()

        # Return results
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to get IP: {response.status_code}")

def get_public_ip():
    response = requests.get("https://api.ipify.org")
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to get IP: {response.status_code}")
    


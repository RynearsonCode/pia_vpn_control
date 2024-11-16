from setuptools import setup, find_packages

setup(
    name="pia_vpn_control",
    version="0.1",
    description="Python Wrapper for The Private Internet Access desktop client command-line interface. Can be used to control some functionality of the PIA client from scripts.",
    author="Sam Rynearson",
    author_email="s.c.rynearson@gmail.com",
    packages=find_packages(),
    install_requires=['requests'],
    python_requires='>=3.6',
)
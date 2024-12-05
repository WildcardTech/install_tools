import os
import subprocess

def install_packages():
    # Packages to install
    packages = ["lldpd", "wireshark", "snmp", "snmpd", "vlan", "bridge-utils", "nmap", "net-tools"]
    
    # Check if the script is running with root privileges
    if os.geteuid() != 0:
        print("Please run this script as root or use sudo.")
        return
    
    try:
        print("Preconfiguring Wireshark to allow non-superusers to capture packets...")
        # Set debconf configuration for Wireshark
        subprocess.run(
            ["echo", "wireshark-common wireshark-common/install-setuid boolean true", "|", "debconf-set-selections"],
            check=True,
            shell=True,
        )
        
        print("Updating package list...")
        subprocess.run(["apt", "update"], check=True)
        
        print("Installing packages...")
        subprocess.run(["apt", "install", "-y"] + packages, check=True)
        print("Installation complete.")
        
        print("Configuring SNMP...")
        subprocess.run(["systemctl", "enable", "snmpd"], check=True)
        subprocess.run(["systemctl", "start", "snmpd"], check=True)
        print("SNMP service configured and started.")
        
        print("Loading 8021q module for VLAN support...")
        subprocess.run(["modprobe", "8021q"], check=True)
        print("VLAN module loaded.")
        
        # Add user to the wireshark group
        current_user = os.getenv("SUDO_USER", os.getenv("USER"))
        if current_user:
            print(f"Adding {current_user} to the wireshark group...")
            subprocess.run(["adduser", current_user, "wireshark"], check=True)
            print(f"User {current_user} has been added to the wireshark group.")
            print("You need to log out and log back in for this change to take effect.")
        else:
            print("Could not determine the current user to add to the wireshark group.")
        
        # Ensure dumpcap is executable
        print("Making /usr/bin/dumpcap executable...")
        subprocess.run(["chmod", "+x", "/usr/bin/dumpcap"], check=True)
        print("/usr/bin/dumpcap is now executable.")
        
        print("Installation of Nmap and net-tools complete.")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing or configuring packages: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    install_packages()

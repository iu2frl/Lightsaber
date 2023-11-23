"""
Deployment script to the target device
A "-p" flag can be set in order to deploy only *.py files
"""

import os
import shutil
import sys
import pyudev
import psutil

def find_circuitpython() -> str:
    """Find the mount point of CIRCUITPYTHON"""
    context = pyudev.Context()
    removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
    for device in removable:
        partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
        #print(f"All removable partitions: {", ".join(partitions}"))
        #print("Mounted removable partitions:")
        for p in psutil.disk_partitions():
            if p.device in partitions:
                if "CIRCUITPY" in p.mountpoint:
                    return p.mountpoint
                #print(f"\t{p.device}: {p.mountpoint}")

def deploy_to_pi(only_py: bool = False):
    """Deploy to target. If argument is True, only '*.py' files in root will be copied"""
    path_to_rp = find_circuitpython() + "/"
    if path_to_rp:
        for file_path in os.listdir("./"):
            if (only_py and file_path.endswith(".py") or not only_py) and os.path.basename(__file__) not in file_path:
                if os.path.isfile(file_path):
                    print(f"Copying file {file_path} to {path_to_rp}")
                    shutil.copyfile(file_path, f"{path_to_rp}/{file_path}")
                else:
                    print(f"Copying folder {file_path} to {path_to_rp}")
                    if "venv" not in file_path:
                        shutil.copytree(file_path, path_to_rp + file_path)
    else:
        print("Could not find CIRCUITPYTHON mount point")

# Execution method
if __name__ == "__main__":
    if "-p" in sys.argv:
        print("Deploying only *.py files")
        deploy_to_pi(True)
    else:
        print("Deploying all files")
        deploy_to_pi(False)
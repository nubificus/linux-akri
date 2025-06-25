import connexion
from typing import Dict
from typing import Tuple
from typing import Union
from flask import Response, jsonify
import subprocess

from openapi_server.models.device_info import DeviceInfo  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.update_request import UpdateRequest  # noqa: E501
from openapi_server import util

import uuid

import psutil
import socket

_cached_mac_address = None

def get_primary_mac_address():
    global _cached_mac_address
    if _cached_mac_address is not None:
        return _cached_mac_address

    try:
        # Create a dummy socket to infer the default IP/interface
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]

        for iface_name, iface_addrs in psutil.net_if_addrs().items():
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and addr.address == local_ip:
                    # Find MAC address on the same interface
                    for a in iface_addrs:
                        if a.family == psutil.AF_LINK:
                            _cached_mac_address = a.address
                            return _cached_mac_address

        raise RuntimeError("Could not determine MAC address for active interface.")
    except Exception as e:
        raise RuntimeError(f"Failed to get MAC address: {e}")

def info_get():  # noqa: E501
    """Get device information

    Retrieve static information about the IoT device. # noqa: E501


    :rtype: Union[DeviceInfo, Tuple[DeviceInfo, int], Tuple[DeviceInfo, int, Dict[str, str]]
    """
    return {
        "device": "rpi5-5",
        "application": "generic",
        "version": "0.0.10"
    }


def onboard_get() -> Union[Response, Tuple[Response, int], Tuple[Response, int, Dict[str, str]]]:
    try:
        # Run your external C binary that generates a PEM certificate
        macaddr = get_primary_mac_address()
        print(macaddr)
        result = subprocess.run(
            ["./bin/gen_cert", macaddr, "--pem"],
            check=True,
            capture_output=True,
            text=False,
        )

        pem_output = result.stdout
        return Response(pem_output, mimetype='application/binary')

    except subprocess.CalledProcessError as e:
        error_response = jsonify({
            "error": "Certificate generation failed",
            "details": e.stderr.strip() if e.stderr else "Unknown error"
        })
        return error_response, 500


def update_post(body):  # noqa: E501
    """Start OTA firmware update

    Initiates an Over-the-Air update using the provided image and optional arguments. # noqa: E501

    :param update_request: 
    :type update_request: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    update_request = body
    if connexion.request.is_json:
        update_request = UpdateRequest.from_dict(connexion.request.get_json())  # noqa: E501
        img = update_request.docker_image
        print("Docker image to use: ", img)

        name = "workload"
        try:
            inspect = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", name],
                capture_output=True,
                text=True
            )
            if inspect.returncode != 0:
                print("Container `workload` does not exist, continue")
            else:
                if inspect.stdout.strip() == "true":
                    print("The container runs, killing it..")
                    subprocess.run(["docker", "kill", name], check=True)

                print("Deleting the container..")
                subprocess.run(["docker", "container", "rm", name], check=True)

        except Exception:
            pass

        subprocess.Popen(
            ["docker", "run", "--name", name, img],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        return 'Container was initiated with the provided image!'

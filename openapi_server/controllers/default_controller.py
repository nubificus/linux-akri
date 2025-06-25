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
import ssl

def img_from_agent(ip: str, port: int, att_crt: str, server_crt_path: str) -> str:
    """
    Establishes a TLS connection, sends the attestation certificate as a string, and returns the server's response.

    Args:
        ip (str): IP address of the server.
        port (int): Port of the server.
        att_crt (str): Attestation certificate (string) to send.
        server_crt_path (str): Path to the server's certificate for TLS verification.

    Returns:
        str: Response from the server, or empty string if the connection is closed.
    """
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(server_crt_path)

    try:
        with socket.create_connection((ip, port)) as sock:
            with context.wrap_socket(sock, server_hostname="ota-agent") as ssock:
                ssock.sendall(att_crt)
                response = ssock.recv(4096)
                return response.decode() if response else ""
    except (ssl.SSLError, socket.error) as e:
        print(f"TLS connection error: {e}")
        return ""

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

def gen_att_cert():
    try:
        macaddr = get_primary_mac_address()
        print(macaddr)
        result = subprocess.run(
            ["./bin/gen_cert", macaddr, "--pem"],
            check=True,
            capture_output=True,
            text=False,
        )
        return result.stdout, 200
    except subprocess.CalledProcessError as e:
        print("Certificate generation failed")
        return "Details: " + e.stderr.strip() if e.stderr else "Unknown error", 500
        return error_response, 500

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
    att, code = gen_att_cert()
    if code == 200:
        return Response(att, mimetype='application/binary')
    else:
        error_response = jsonify({
            "error": "Certificate generation failed",
            "details": att
        })
        return error_response, code


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
        if img == "":
            args = update_request.args
            if args != None and "--ip" in args:
                ip_index = args.index("--ip")
                if ip_index + 1 >= len(args):
                    status = "Invalid --ip argument in end of the argument list"
                    print(status)
                    return status

                ip = args[ip_index + 1]
                print("Agent IP: ", ip)

                port = 4433
                server_crt_path = "./crt/cert.pem"
                att, code = gen_att_cert()
                if code != 200:
                    error_response = jsonify({
                        "error": "Certificate generation failed",
                        "details": att
                    })
                    return error_response, code

                img = img_from_agent(ip, port, att, server_crt_path)
                if img == "":
                    status = "Could not get the image from Agent"
                    print(status)
                    return status
            else:
                status = "Empty docker image in JSON, and no IP given (--ip)"
                print(status)
                return status

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

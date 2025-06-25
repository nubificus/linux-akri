#!/usr/bin/env python3

import connexion
import os
import urllib.request
import platform
from openapi_server import encoder

def on_startup():
    gen_cert_path = "./bin/gen_cert"

    if os.path.exists(gen_cert_path):
        print("gen_cert executable already exists. Skipping download.")
        return

    os.makedirs("./bin", exist_ok=True)

    arch_raw = platform.machine()
    if arch_raw == "x86_64":
        arch = "amd64"
    elif arch_raw == "aarch64":
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {arch_raw}")

    url = f"https://s3.nbfc.io/nbfc-assets/github/dice/auth/{arch}/gen_cert"
    print(f"Downloading gen_cert executable for architecture '{arch}' from:\n{url}")

    try:
        urllib.request.urlretrieve(url, gen_cert_path)
        os.chmod(gen_cert_path, 0o755)
        print("gen_cert downloaded and marked as executable.")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch gen_cert: {e}")

def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Generic IoT Device API'},
                pythonic_params=True)

    on_startup()
    app.run(port=8080)


if __name__ == '__main__':
    main()

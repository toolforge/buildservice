#!/usr/bin/env python3
"""
Dummy script to remove the https yaml section from the harbor config template.
"""
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import yaml


def set_hostname(config: Dict[str, Any]) -> Dict[str, Any]:
    config["hostname"] = subprocess.check_output("hostname -I| awk '{print $1}'", shell=True).decode().strip()
    return config


def generate_ssl_certs(config: Dict[str, Any], dst_dir: Path) -> Dict[str, Any]:
    private_key_path = dst_dir / "server-key.pem"
    cert_path = dst_dir / "server.pem"
    conf_path = dst_dir / "csr.conf"
    with conf_path.open("w") as conf_fd:
        conf_fd.write(
            """
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
prompt = no
[req_distinguished_name]
C = US
ST = VA
L = SomeCity
O = MyCompany
OU = MyDivision
CN = MyCN
[v3_req]
basicConstraints = CA:FALSE
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = host.minikube.internal
IP = 192.168.49.1
"""
        )

    subprocess.check_call(
        [
            "openssl",
            "req",
            "-x509",
            "-nodes",
            "-days",
            "730",
            "-newkey",
            "rsa:2048",
            "-keyout",
            private_key_path,
            "-out",
            cert_path,
            "-config",
            conf_path,
            "-extensions",
            "v3_req",
        ]
    )
    config["https"]["certificate"] = str(cert_path.resolve())
    config["https"]["private_key"] = str(private_key_path.resolve())
    return config


def main() -> int:
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("harbor_src_path", help="Path to the harbor source code.", type=Path)
    args = parser.parse_args()
    tmpl_path = args.harbor_src_path / "harbor.yml.tmpl"
    config = yaml.safe_load(tmpl_path.open())
    config = set_hostname(config)
    # self-signed certs are not yet supported, see https://github.com/buildpacks/lifecycle/issues/524
    # config = generate_ssl_certs(config, dst_dir=args.harbor_src_path)
    del config["https"]
    # this will store all the generated data
    config["data_volume"] = str(Path("data").resolve())
    cfg_path = args.harbor_src_path / "harbor.yml"
    cfg_path.open("w").write(yaml.safe_dump(config))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
import sys

import requests


def main() -> int:
    harbor_url = "http://127.0.0.1/api/v2.0"
    projects_url = f"{harbor_url}/projects"
    project_name = "minikube-user"
    response = requests.get(url=projects_url, params={"name": project_name})
    response.raise_for_status()
    if response.json():
        print(f"The project {project_name} already exists, skipping it's creation.")
        return 0

    new_project_object = {
        "project_name": project_name,
        "public": True,
        "metadata": {"public": "true", "prevent_vul": "false", "auto_scan": "false"},
        "storage_limit": -1,
    }

    response = requests.post(url=projects_url, json=new_project_object, auth=("admin", "Harbor12345"))
    response.raise_for_status()
    print(f"The project {project_name} was created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

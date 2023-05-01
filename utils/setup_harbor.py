#!/usr/bin/env python3
import sys
from typing import Tuple

import requests


def ensure_project_exsits(harbor_url: str, admin_auth: Tuple[str, str]):
    projects_url = f"{harbor_url}/projects"
    project_name = "tool-minikube-user"
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

    response = requests.post(url=projects_url, json=new_project_object, auth=admin_auth)
    response.raise_for_status()
    print(f"The project {project_name} was created.")
    return


def ensure_robot_account_exists(harbor_url: str, admin_auth: Tuple[str, str]):
    robots_url = f"{harbor_url}/robots"
    robot_name = "tekton"
    response = requests.get(url=robots_url, auth=admin_auth)
    response.raise_for_status()
    if response.json():
        maybe_robot = next((robot for robot in response.json() if robot["name"] == f"robot${robot_name}"), None)
    else:
        maybe_robot = None

    if maybe_robot is None:
        new_robot_object = {
            "name": robot_name,
            "secret": "Dummyr0botpass",
            "disable": False,
            "level": "system",
            "duration": -1,
            "description": "Tekton pipelines pushing robot account",
            "permissions": [
                {
                    "access": [
                        {"action": "push", "resource": "repository"},
                        {"action": "pull", "resource": "repository"},
                        {"action": "delete", "resource": "artifact"},
                        {"action": "read", "resource": "helm-chart"},
                        {"action": "create", "resource": "helm-chart-version"},
                        {"action": "delete", "resource": "helm-chart-version"},
                        {"action": "create", "resource": "tag"},
                        {"action": "delete", "resource": "tag"},
                        {"action": "create", "resource": "artifact-label"},
                        {"action": "create", "resource": "scan"},
                    ],
                    "kind": "project",
                    "namespace": "*",
                }
            ],
        }

        response = requests.post(url=robots_url, json=new_robot_object, auth=admin_auth)
        response.raise_for_status()
        robot_id = response.json()["id"]
    else:
        print(f"Robot account robot${robot_name} already exists, skipping creation")
        robot_id = maybe_robot["id"]

    secret_request_obj = {"secret": "Dummyr0botpass"}
    response = requests.patch(url=f"{robots_url}/{robot_id}", json=secret_request_obj, auth=admin_auth)
    response.raise_for_status()
    print(f"The robot account robot${robot_name} was created and pass set to 'Dummyr0botpass'.")
    return


def main() -> int:
    harbor_url = "http://127.0.0.1/api/v2.0"
    admin_auth = ("admin", "Harbor12345")
    ensure_project_exsits(harbor_url, admin_auth=admin_auth)
    ensure_robot_account_exists(harbor_url, admin_auth=admin_auth)
    return 0


if __name__ == "__main__":
    sys.exit(main())

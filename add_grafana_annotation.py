#!/usr/bin/python

DOCUMENTATION = """
---
module: add_grafana_annotation
short_description: Add Grafana annotations
"""

DOCUMENTATION = """
---
module: add_grafana_annotation

short_description: Add Grafana annotations

version_added: "2.9"

description:
    - "A module used to create annotations in Grafana dashboards/panels."

options:
    grafana_api_url:
        description:
            - FQDN of the Grafana API host (e.g. https://grafana.sample.net)
        required: true
    grafana_api_key:
        description:
            - API key for Grafana (with Editor access)
        required: true
    dashboard_id:
        description:
            - The dashboard to annotate, by ID (if none specified, global annotation). Mutually exclusive with `dashboard_name`.
        required: false
    dashboard_name:
        description:
            - The dashboard to annotate, by name (if none specified, global annotation). Mutually exclusive with `dashboard_id`.
        required: false
    panel_id:
        description:
            - The panel ID to annotate (if dashboard is specified but no panel, all panels will be annotated)
        required: false
    text:
        description:
            - Text to add to the annotation
        required: true
    tags:
        description:
            - Tags to add to the annotation, in list format
        required: false


extends_documentation_fragment
    - grafana

author:
    - Alexandros Orfanos (@aorfanos)
"""

EXAMPLES = """
- name: Create a Grafana annotation
  add_grafana_annotation:
    grafana_api_url: "https://grafana.myproject.com"
    grafana_api_key: "..."
    dashboard_id: 468
    panel_id: 20
    text: "Annotation description"
    tags:
      - tag1
      - tag2
  register: result
"""

RETURN = """
remote_status_code:
    description: The HTTP return code of the RESTFul call to Grafana API
    type: int
message:
    description: An auxiliary message, containing the return code and (very) basic troubleshooting info
"""

ANSIBLE_METADATA = {
    "status": ["preview"],
    "supported_by": "community",
    "metadata_version": "1.0",
}

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime
import time
import requests
import json
import urllib.request as urllib


def create_timestamp():
    _date = datetime.now()
    return int(_date.timestamp()) * 1000


def get_dashboard_by_name(dashboardName, grafanaApiUrl, authHeaders):
    _url = "{}/api/search?query={}".format(
        grafanaApiUrl, urllib.quote(dashboardName, safe="")
    )
    result = requests.get(_url, headers=authHeaders).json()
    for res in result:
        return res["id"]


def run_module():

    module_args = dict(
        grafana_api_url=dict(type="str", required=True),
        grafana_api_key=dict(type="str", required=True, no_log=True),
        dashboard_id=dict(type="int", required=False),
        dashboard_name=dict(type="str", required=False),
        panel_id=dict(type="int", required=False),
        text=dict(type="str", required=True),
        tags=dict(type="list", required=False, elements="str"),
    )

    result = dict(changed=False, remote_status_code="", message="")

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    headers = {
        "Authorization": "Bearer {}".format(module.params["grafana_api_key"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    url = "{}{}".format(module.params["grafana_api_url"], "/api/annotations")

    if module.check_mode:
        return result

    data = {
        "time": create_timestamp(),
        "text": module.params["text"],
    }

    if module.params["dashboard_name"]:
        _dashboard_id = get_dashboard_by_name(
            module.params["dashboard_name"], module.params["grafana_api_url"], headers
        )
        if _dashboard_id is None:
            module.fail_json(msg="Dashboard name does not exist", **data)
        else:
            data["dashboardId"] = _dashboard_id
    if module.params["dashboard_id"]:
        data["dashboardId"] = module.params["dashboard_id"]
    if module.params["panel_id"]:
        data["panelId"] = module.params["panel_id"]
    if module.params["tags"]:
        data["tags"] = module.params["tags"]

    _result = requests.post(url, json.dumps(data), headers=headers)

    if _result.status_code == 200:
        result["changed"] = True
        result["remote_status_code"] = _result.status_code
        result["message"] = "OK"
    elif _result.status_code > 399 or _result.status_code < 499:
        result["changed"] = False
        result["remote_status_code"] = _result.status_code
        result["message"] = "Probably a request issue (return code: {})".format(
            _result.status_code
        )
    elif _result.status_code > 499 or _result.status_code < 599:
        result["changed"] = False
        result["remote_status_code"] = _result.status_code
        result["message"] = "Server-side issue (return code: {})".format(
            _result.status_code
        )
    else:
        result["changed"] = False
        result["remote_status_code"] = _result.status_code
        result["message"] = "Unknown issue (return code: %s)".format(
            _result.status_code
        )

    if result["changed"] == False:
        module.fail_json(msg="Create annotation failed", **result)

    module.exit_json(**result, **data)


def main():
    run_module()


if __name__ == "__main__":
    main()

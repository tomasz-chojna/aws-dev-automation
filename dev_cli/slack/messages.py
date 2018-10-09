import json

import requests

from dev_cli.settings.main import SLACK_WEBHOOK_URL


def send_notification_about_new_server(host):
    payload = {
        "attachments": [
            {
                "color": "#36a64f",
                "author_name": "AWS Dev CLI",
                "title": "New dev server has been provisioned - {}".format(host),
            }
        ]
    }

    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={'Content-type': 'application/json'})

import json

import requests


def send_to_slack_message(message):
    webhook_url = 'https://hooks.slack.com/services/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'
    requests.post(
        webhook_url,
        data=json.dumps({'blocks': message}),
        headers={'Content-Type': 'application/json'}
    )

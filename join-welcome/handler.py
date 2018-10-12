import sys
import json
import random
import os

import requests

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    log_event(req)

    if os.getenv("log_env", "0") == "1":
        log_env()

    r = None
    try:
        r = json.loads(req)
    except json.decoder.JSONDecodeError:
        sys.stderr.write("Error parsing request, invalid JSON")
        os.exit(1)

    if "challenge" in r:
        return challenge(r)

    with open("/var/openfaas/secrets/slack-incoming-webhook-url") as webhook_url_text:
        webhook_url = webhook_url_text.read().strip()

        if "event" in r:
            target_channel = os.getenv("target_channel")
            return process_event(r, target_channel, webhook_url)

    return "Nothing to do with webhook"

def challenge(r):
    if r["type"] == "url_verification":
        res = {"challenge": r["challenge"]}
        return json.dumps(res)

def process_event(r, target_channel, webhook_url):
    event_type = r["event"]["type"]

    if r["event"]["channel"] == target_channel:
        if event_type == "member_joined_channel":
            if "user" in r["event"]:
                user_name = r["event"]["user"]
                who = "<@{}>".format(user_name)

                positive_emoticons = [":openfaas:", ":whale:", ":thumbsup:", ":wave:", ":sunglasses:", ":ok_hand:", ":chart_with_upwards_trend:", ":sunrise:", ":smiley:", ":smiley_cat:", ":parrot:", ":rocket:", ":100:", ":muscle:", ":signal_strength:", ":man-cartwheeling:"]

                emoticons = build_emoticons(positive_emoticons)

                msg = {"text": "Let's all welcome {} to the community! {} ".format(who, emoticons.strip())}

                out_req = requests.post(webhook_url, json=msg)
                return ("{} response from Slack: {}".format(str(out_req.status_code), out_req.text))

    return "Cannot process event_type: {}".format(event_type)

def build_emoticons(emoticons):
    emoticon_str = ""
    sample = random.sample(emoticons, 5)

    for emoticon in sample:
        emoticon_str = emoticon_str + emoticon + " "

    return emoticon_str

def log_event(req):
    sys.stderr.write(req)

def log_env():
    envs = os.environ
    for e in envs:
        sys.stderr.write(e + " " + envs[e] + "\n")

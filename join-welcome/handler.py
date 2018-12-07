import sys
import os
import random
import json
from hashlib import sha256
import hmac
from time import perf_counter

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
    except ValueError:
        sys.stderr.write("Error parsing request, invalid JSON")
        return
        # sys.exit(1)

    if "challenge" in r:
        return challenge(r)

    if "event" in r:
        webhook_url = read_secret("slack-incoming-webhook-url")
        signing_secret = read_secret("slack-signing-token")

        target_channel = os.getenv("target_channel")
        digest = os.getenv("Http_X_Slack_Signature", "")

        # Takes format of: "Http_X_Slack_Signature v0=hash"

        slack_request_timestamp = os.getenv("Http_X_Slack_Request_Timestamp", "")

        input = f"v0:{slack_request_timestamp}:{req}"

        start = perf_counter()
        is_valid_hmac = valid_hmac(signing_secret, input, get_hash(digest))
        end = perf_counter()
        elapsed = end - start

        sys.stderr.write("valid_hmac took {}s\n".format(elapsed))

        if is_valid_hmac == True:
            return process_event(r, target_channel, webhook_url)
        else:
            sys.stderr.write("Invalid HMAC in X-Slack-Signature header")
            # sys.exit(1)
            return

    return "Nothing to do with webhook"

def challenge(r):
    if r["type"] == "url_verification":
        res = {"challenge": r["challenge"]}
        return json.dumps(res)


# valid_hmac("key", "value", "90fbfcf15e74a36b89dbdb2a721d9aecffdfdddc5c83e27f7592594f71932481")
def valid_hmac(key, msg, digest):
    hash = hmac.new(key.encode('utf-8'), msg.encode('utf-8'), sha256)
    hexdigest = hash.hexdigest()
    res = digest == hexdigest
    if res == False:
        msg = "Hash - got: '" + digest + "' computed: '" + hexdigest + "' " + str(res) + "\n"
        sys.stderr.write(msg)

    return res

def read_secret(name):
    value = ""
    
    with open("/var/openfaas/secrets/" + name) as f:
        value = f.read().strip()

    return value

# input = "v0=hash"
# print(get_hash(input))
def get_hash(input):
    index = input.find("=")
    if index > -1:
        return input[index+1:]
    return input

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

                start = perf_counter()
                out_req = requests.post(webhook_url, json=msg)
                end = perf_counter()
                elapsed = end - start

                sys.stderr.write("{} response from Slack: {} in {}s\n".format(str(out_req.status_code), out_req.text, elapsed))
                return ("{} response from Slack: {} in {}s".format(str(out_req.status_code), out_req.text, elapsed))

    return "Cannot process event_type: {}".format(event_type)

def build_emoticons(emoticons):
    emoticon_str = ""
    sample = random.sample(emoticons, 5)

    for emoticon in sample:
        emoticon_str = emoticon_str + emoticon + " "

    return emoticon_str

def log_event(req):
    sys.stderr.write(req+"\n")

def log_env():
    envs = os.environ
    for e in envs:
        sys.stderr.write(e + " " + envs[e] + "\n")

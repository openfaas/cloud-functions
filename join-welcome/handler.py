import sys
import os
import random
import json
from hashlib import sha256
import hmac
from time import perf_counter

def handle(event, context):
    SLACK_SIG_HEADER = "X-Slack-Signature"
    SLACK_TIMESTAMP_HEADER = "X-Slack-Request-Timestamp"
    
    # Convert bytestring to python3 default encoding (utf-8)
    body = event.body.decode()

    log_event(body)

    if os.getenv("log_env", "0") == "1":
        log_env()

    r = None
    try:
        r = json.loads(body)
    except ValueError:
        sys.stderr.write("Error parsing request, invalid JSON")
        return {
            "statusCode": 400,
            "body": "Error parsing request, invalid JSON"
        }
    
    if "challenge" in r:
        res = challenge(r)
        return {
            "statusCode": 200,
            "body": res
        }
    if "event" not in r:
        return {
            "statusCode": 400,
            "body": "Nothing to do with webhook"
        }
    
    webhook_url = read_secret("slack-incoming-webhook-url")
    signing_secret = read_secret("slack-signing-token")

    target_channel = os.getenv("target_channel")
    digest = ""
    if SLACK_SIG_HEADER in event.headers:
        digest = event.headers[SLACK_SIG_HEADER]

    # Takes format of: "X-Slack-Signature v0=hash"
    slack_request_timestamp = ""
    if SLACK_TIMESTAMP_HEADER in event.headers:
        slack_request_timestamp = event.headers[SLACK_TIMESTAMP_HEADER]

    input = f"v0:{slack_request_timestamp}:{body}"

    sys.stderr.write("Input: '{}'\n".format(input))

    start = perf_counter()
    is_valid_hmac = valid_hmac(signing_secret, input, get_hash(digest))
    end = perf_counter()
    elapsed = end - start

    sys.stderr.write("valid_hmac took {}s\n".format(elapsed))

    if is_valid_hmac == True:
        start = perf_counter()

        event_res = process_event(r, target_channel, webhook_url)

        end = perf_counter()
        elapsed = end - start
        sys.stderr.write("process_event took {}s\n".format(elapsed))

        return event_res
    else:
        sys.stderr.write("Invalid HMAC in X-Slack-Signature header")
        # sys.exit(1)
        return {
            "statusCode": 401,
            "body": "Invalid HMAC in X-Slack-Signature header"
        }

def challenge(r):
    if r["type"] == "url_verification":
        res = {"challenge": r["challenge"]}
        return res

# valid_hmac("key", "value", "90fbfcf15e74a36b89dbdb2a721d9aecffdfdddc5c83e27f7592594f71932481")
def valid_hmac(key, msg, digest):
    hash = hmac.new(key.encode('utf-8'), msg.encode('utf-8'), sha256)
    hexdigest = hash.hexdigest()
    res = digest == hexdigest
    if res == False:
        msg = "Hash - got: '{}' computed: '{}' {}\n".format(digest, hexdigest, str(res))
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

                start = perf_counter()

                emoticons = build_emoticons(positive_emoticons)
                end = perf_counter()
                elapsed = end - start

                sys.stderr.write("Generating emoticons took {}s\n".format(elapsed))

                msg = {"text": "Let's all welcome {} to the community! {} ".format(who, emoticons.strip())}

                start = perf_counter()
                out_req = requests.post(webhook_url, json=msg)
                end = perf_counter()
                elapsed = end - start

                sys.stderr.write("{} response from Slack: {} in {}s\n".format(str(out_req.status_code), out_req.text, elapsed))
                return {
                    "statusCode": 200,
                    "body": ("{} response from Slack: {} in {}s".format(str(out_req.status_code), out_req.text, elapsed))
                }
    return {
        "statusCode": 400,
        "body": "Cannot process event_type: {} or given channel is not target channel".format(event_type)
    }

def build_emoticons(emoticons):
    sample = random.sample(emoticons, 5)
    return " ".join(sample)

def log_event(req):
    sys.stderr.write("{}\n".format(req))

def log_env():
    envs = os.environ
    for e in envs:
        sys.stderr.write("{} {}\n".format(e, envs[s]))
        
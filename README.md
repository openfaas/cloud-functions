# cloud-functions

Functions used by OpenFaaS Community

## join-welcome

This function is a bot that welcomes anyone who joins the #openfaas channel.

```sh
export slack_incoming_webhook_url="URL"
export slack_token="TOKEN"
export slack_signing_token="SIGNING_TOKEN"

faas-cli cloud seal --name openfaas-cloud-functions-secrets \
    --literal slack-incoming-webhook-url="$slack_incoming_webhook_url" \
    --literal slack-token="$slack_token" \
    --literal slack-signing-token="$slack_signing_token" \
    --cert=./pub-cert.pem
```

## signup

This function redirects to the OpenFaaS Cloud Community Cluster sign-up page.

## slack

Redirects to the Slack sign-up instructions.



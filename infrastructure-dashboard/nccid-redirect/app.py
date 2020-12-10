#!/usr/bin/env python3

from aws_cdk import core

from nccid_redirect.nccid_redirect_stack import NccidRedirectStack


app = core.App()
NccidRedirectStack(app, "nccid-redirect")

app.synth()

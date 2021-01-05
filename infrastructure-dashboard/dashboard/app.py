#!/usr/bin/env python3

from aws_cdk import core

from dashboard.dashboard_stack import DashboardStack


app = core.App()
DashboardStack(app, "nccid-dashboard")

app.synth()

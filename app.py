#!/usr/bin/env python3
import os

import aws_cdk as cdk

from streamlit_service.streamlit_service_stack import StreamlitServiceStack


TAGS = {
    'app': 'Constitucion2023',
    'customer': 'Internal'
}

app = cdk.App()
stk = StreamlitServiceStack(app, "ConstitucionChat")

if TAGS.keys():
    for k in TAGS.keys():
        cdk.Tags.of(stk).add(k, TAGS[k])
app.synth()

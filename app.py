#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAI-env Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

import os
import socket
import flask
import redis

# Connect to Redis
redis = redis.Redis(host="redis", db=0)

app = flask.Flask(__name__)


@app.route("/")
def hello():
    """

    Returns:
              html.format()
    """
    try:
        visits = redis.incr('counter')
    except redis.RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = '<h3>Hello {name}!</h3>' '<b>Hostname:</b> {hostname}<br/>' '<b>Visits:</b> {visits}'
    return html.format(name=os.getenv('NAME', "world"), hostname=socket.gethostname(), visits=visits)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

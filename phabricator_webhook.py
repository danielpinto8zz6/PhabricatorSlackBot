#!/usr/bin/env python3

import sys

import argparse
import logging
import os
from flask import Flask, request, abort, jsonify

from slack_api import SlackApi

app = Flask(__name__)
args = None
slack_api = None


@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        message = request.json['message']

        if (message):
            slack_api.send_message("#phabricator", message)

        return jsonify({'status': 'success'}), 200
    else:
        abort(400)


@app.route('/', methods=['GET'])
def query_string_index():
    if request.method == 'GET':
        message = request.args.get("message", default="", type=str)

        if (message):
            slack_api.send_message("#phabricator", message)
            
        return jsonify({'status': 'success'}), 200
    else:
        abort(400)


def main():
    global args  # pylint: disable=global-statement
    global slack_api # pylint: disable=global-statement

    parser = argparse.ArgumentParser(
        description="Creates and updates Maniphest tasks for alerts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-p", "--port", type=int, default=8292, help="Port to bind to")
    parser.add_argument(
        "-b", "--bind", default="localhost", help="Host to bind to")
    parser.add_argument(
        "-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO, help="Enable debug logging")

    args = parser.parse_args()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s", level=args.loglevel)

    slack_token = os.environ.get("SLACK_TOKEN")
    if not slack_token:
        print("SLACK_TOKEN not set")
        sys.exit(1)

    slack_api = SlackApi(slack_token)

    app.run(host=args.bind, port=args.port)


if __name__ == "__main__":
    main()

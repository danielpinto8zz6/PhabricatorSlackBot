#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from flask import Flask, request, abort

from phabricator_api import Phabricator, Subscriable
from slack_api import SlackApi

app = Flask(__name__)
args = None
slack_api = None
phabricator_host = None
phabricator_user = None
phabricator_cert = None
phabricator = None


@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        author_phid = request.form.get('storyAuthorPHID')
        story_id = request.form.get('storyID')
        object_phid = request.form.get('storyData[objectPHID]')
        story_text = request.form.get('storyText')

        if object_phid is None:
            resp = 'Unsupported story: %r' % request.form
            logging.info(resp)
            return resp

        ph_obj = phabricator.get_object_by_phid(object_phid)

        if not isinstance(ph_obj, Subscriable):
            resp = "Unsupported object: %s" % object_phid
            return resp

        msg = u'%s Click to view：%s' % (story_text, ph_obj.url)
        slack_api.send_message("#phabricator", msg)

        return 'success'
    else:
        abort(400)


def main():
    global args  # pylint: disable=global-statement
    global slack_api  # pylint: disable=global-statement
    global phabricator_host  # pylint: disable=global-statement
    global phabricator_user  # pylint: disable=global-statement
    global phabricator_cert  # pylint: disable=global-statement
    global phabricator  # pylint: disable=global-statement

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

    phabricator_host = os.environ.get("PHABRICATOR_HOST")
    if not phabricator_host:
        print("PHABRICATOR_HOST not set")
        sys.exit(1)

    phabricator_user = os.environ.get("PHABRICATOR_USER")
    if not phabricator_user:
        print("PHABRICATOR_USER not set")
        sys.exit(1)

    phabricator_cert = os.environ.get("PHABRICATOR_CERT")
    if not phabricator_cert:
        print("PHABRICATOR_CERT not set")
        sys.exit(1)

    phabricator = Phabricator(host=phabricator_host, username=phabricator_user, cert=phabricator_cert)

    slack_api = SlackApi(slack_token)

    app.run(host=args.bind, port=args.port)


if __name__ == "__main__":
    main()
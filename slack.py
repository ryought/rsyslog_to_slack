#!/usr/bin/env python3
import sys
import json
import urllib.request
import argparse


def post(url, data):
    """post data (dict) as JSON to specified URL."""
    headers = {
        'Content-Type': 'application/json',
    }
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
            return body
    except urllib.error.URLError as e:
        print(e, file=sys.stderr)


def loop(url):
    def on(messages):
        print('messages', len(messages))
        data = {
            'text': '\n'.join(messages),
        }
        ret = post(url, data)
        print(ret, file=sys.stderr)
        return

    queue = None
    while True:
        message = sys.stdin.readline()
        # remove \n at the end
        message = message.rstrip()
        # EOF should stop this daemon
        if not message:
            break
        if message.startswith('BEGIN TRANSACTION'):
            queue = []
        elif message.startswith('COMMIT TRANSACTION'):
            on(queue)
            queue = None
        else:
            if queue is not None:
                # within transaction
                queue.append(message)
            else:
                # single message without transaction mode
                on([message])


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('URL', type=str, help='Slack Incoming Webhook URL (e.g. https://hooks.slack.com/services/XXXXX/YYYYY/ZZZZZ)')
    args = parser.parse_args()
    loop(args.URL)


main()
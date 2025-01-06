#!/usr/bin/env python3
import sys
import json
import urllib.request
import argparse
import re

def post(url, data, proxy=None):
    """post data (dict) as JSON to specified URL."""
    headers = {
        'Content-Type': 'application/json',
    }
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    if proxy is not None:
        proxy_handler = urllib.request.ProxyHandler({'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
            return body
    except urllib.error.URLError as e:
        print(e, file=sys.stderr)


def loop(url, proxy=None, ignore_patterns=[]):
    def ignored(text):
        for pattern in ignore_patterns:
            if re.match(pattern, text):
                return True
        return False
    def on(messages):
        messages = [message for message in messages if not ignored(message)]
        # print(messages)
        if len(messages) == 0:
            return
        data = {
            'text': '\n'.join(messages),
        }
        ret = post(url, data, proxy)
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

DEFAULT_IGNORE_PATTERNS = [
    # sshd
    '.*maximum authentication attempts exceeded.*',
    '.*ssh_packet_get_string: incomplete message.*',
    # systemd-networkd-wait-online
    '.*systemd-networkd-wait-online.*Timeout occurred while waiting for network connectivity.*',
    # anacron/sendmail
    '.*Can\'t find sendmail at /usr/sbin/sendmail, not mailing output.*',
]

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('URL', type=str, help='Slack Incoming Webhook URL (e.g. https://hooks.slack.com/services/XXXXX/YYYYY/ZZZZZ)')
    parser.add_argument('--proxy', default=None, type=str, help='HTTPS proxy URL (e.g. proxy.example.com:8080)')
    parser.add_argument('--ignore', nargs='*', type=str, default=DEFAULT_IGNORE_PATTERNS,
                        help='Lines that match with regexp pattern(s) will be ignored')
    args = parser.parse_args()
    loop(args.URL, args.proxy, args.ignore)


main()

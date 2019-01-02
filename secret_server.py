import math
import re
import sys
import time
import urllib.parse
from flask import Flask, request
from flask_cors import CORS

APP = Flask(__name__)
CORS(APP)


RECENT_IP_ADDRESSES = dict()
REQUEST_COOLDOWN_SECONDS = 0.5


@APP.route('/')
def reveal_secret():
    ip_address = request.remote_addr
    print()
    print(f"Received request from {ip_address}")
    if _should_accept(ip_address):
        return _attempt_to_handle(request)
    else:
        seconds_to_wait = math.ceil(_seconds_to_wait(ip_address))
        return f"You've used this service recently. Please try again after {seconds_to_wait} seconds."


def _should_accept(ip_address):
    if ip_address in RECENT_IP_ADDRESSES:
        return _seconds_to_wait(ip_address) <= 0
    else:
        return True


def _seconds_to_wait(ip_address):
    current_seconds = time.time()
    seconds_of_last_request = RECENT_IP_ADDRESSES[ip_address]
    elapsed_seconds = current_seconds - seconds_of_last_request
    return REQUEST_COOLDOWN_SECONDS - elapsed_seconds


def _attempt_to_handle(request):
    ip_address = request.remote_addr
    RECENT_IP_ADDRESSES.pop(ip_address, None)
    try:
        return _handle(request)
    except KeyError as e:
        return "No secret was provided in the request! Ask Brandon for help."
    finally:
        RECENT_IP_ADDRESSES[ip_address] = time.time()


def _handle(request):
    secret = urllib.parse.unquote(str(request.args["secret"]))
    print(f"Received Secret: {secret}")

    filename = f"secrets/{secret}.secret"
    print(f"Filename is: {filename}")

    try:
        with open(filename, 'r') as f:
            print("Success. Read file.")
            contents = f.read()
            contents = re.sub("(?i)</html>", "", contents)
            script = "<script>parent.postMessage('resizeIframe', 'foo');console.log('Yeet');</script>"
            return contents + "\n" + script + "\n" + "</html>"
    except FileNotFoundError:
        print("Nothing found.")
        return f"No secret found for '{secret}'. Try something else."

    return "Hello"


if __name__ == '__main__':
    ssl_directory = sys.argv[1]
    ssl_file = lambda path: ssl_directory + '/' + path
    ssl_context = (ssl_file('fullchain.pem'), ssl_file('privkey.pem'))
    print(ssl_context)
    APP.run(host="0.0.0.0", port=5001, threaded=True, ssl_context=ssl_context)


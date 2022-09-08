#!/usr/bin/env python3

"""
A Sentieon license server extension script, https://support.sentieon.com/appnotes/license_server/
"""

import base64
import json
import os.path
import sys

import license_message

EXPECTED_MESSAGE = "Secret message"
LICENSE_KEY_FILE = os.path.join(os.path.expanduser("~"), ".sentieon/license_key.txt")

def main(argv):
    request_data = json.load(sys.stdin)
    mech = request_data.get("mech")
    if mech == "GitHub Actions - token":
        try:
            license_key = open(LICENSE_KEY_FILE).read().rstrip()
            key = base64.b64decode(license_key.encode("utf-8"))
        except:
            print("Unable to read license key", file=sys.stderr)
            return -1

        try:
            ciphertext = request_data.get("data")
            ciphertext = base64.b64decode(ciphertext.encode("utf-8"))
        except:
            print("Unable to parse ciphertext", file=sys.stderr)
            return -1

        try:
            message = license_message.decrypt_message(key, ciphertext)
        except DecryptionTimeout as err:
            print("Error due to a timeout", file=sys.stderr)
            return -1
        except:
            print("Error during message decryption", file=sys.stderr)
            return -1

        if message != EXPECTED_MESSAGE:
            return -1
        return 0

    else:
        print("Unknown AUTH_MECH: " + str(mech), file=sys.stderr)
        return -1

if __name__ == "__main__":
    sys.exit(main(sys.argv))

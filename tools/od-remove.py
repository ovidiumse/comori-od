#!/usr/bin/pypy3
import os
import argparse
import logging
import requests
from getpass import getpass

PARSER_ = argparse.ArgumentParser(description="OD content remover.")

COMORI_OD_API_HOST = ""
API_OTPKEY = ""


def parseArgs():
    group = PARSER_.add_mutually_exclusive_group(required=True)
    group.add_argument("--volume", dest="volume", action="store", type=str, help="Volume to remove")
    group.add_argument("--book", dest="book", action="store", type=str, help="Book to remove")
    PARSER_.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Verbose logging")

    args, _ = PARSER_.parse_known_args()
    return args


def delete(uri):
    response = requests.delete(
        f"{COMORI_OD_API_HOST}/{uri}",
        headers={"Authorization": f"Token {API_OTPKEY}"})
    
    response.raise_for_status()


def remove_volume(volume):
    try:
        delete(f"od/volumes/{volume}")
    except Exception as ex:
        logging.error(f"Removing volume {volume} failed! Error: {ex}", exc_info=True)


def remove_book(book):
    try:
        delete(f"od/books/{book}")
    except Exception as ex:
        logging.error(f"Removing book {book} failed! Error: {ex}", exc_info=True)


def main():
    args = parseArgs()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    global COMORI_OD_API_HOST
    COMORI_OD_API_HOST = os.getenv("COMORI_OD_API_HOST", "http://localhost:9000")

    print(f"API HOST: {COMORI_OD_API_HOST}")

    global API_OTPKEY
    if "API_TOTP_KEY" in os.environ:
        API_OTPKEY = os.getenv("API_TOTP_KEY")
    else:
        API_OTPKEY = getpass("OTP code: ")
        os.environ["API_TOTP_KEY"] = API_OTPKEY

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if args.volume:
        remove_volume(args.volume)
    elif args.book:
        remove_book(args.book)

if "__main__" == __name__:
    main()
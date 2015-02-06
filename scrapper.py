#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
import argparse
from datetime import datetime
import re
from time import time, sleep

from bs4 import BeautifulSoup
from pushbullet import PushBullet
import requests
from requests.exceptions import RequestException

import config

parser = argparse.ArgumentParser()

parser.add_argument('-r', '--regex', dest='regex', help='Regex to match')
parser.add_argument('-u', '--url', dest='url', help='URL to check')
parser.add_argument('-m', '--mode', dest='mode', help='Mode for matching (FOUND or NOT_FOUND')

args = parser.parse_args()

HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

REGEX_FOUND_MESSAGE = "Regex found"
REGEX_NOT_FOUND_MESSAGE = "Regex not found"


def get_response_from_site(site_url):

    site_response = None

    try:
        print "Contacting site at {url}...".format(url=site_url)
        site_response = requests.get(site_url, headers=HEADERS, timeout=30)
    except RequestException as e:
        print "Got an error trying to reach site.", e.message
        exit(-1)

    print "Got data from site"

    return site_response


def send_notification(api_key, page_title, site_url):

    print "Sending PushBullet notification"

    pb_client = PushBullet(api_key)

    pb_client.push_link("Update on {title}!".format(title=page_title), site_url)


def main():

    config.check_config_file()
    app_config = config.load_config_file()
    pushbullet_api_key = app_config.get('api_key')

    regex_to_test = getattr(args, 'regex', app_config.get('regex'))
    if regex_to_test:
        regex_to_test = re.compile(regex_to_test)
    site_url = getattr(args, 'url', app_config.get('site_to_parse'))
    if getattr(args, 'mode', False):
        match_if_present = False if getattr(args, 'mode', None) == 'NOT_FOUND' else True
    else:
        match_if_present = False if app_config.get('match_mode') == 'NOT_FOUND' else True

    if not pushbullet_api_key or not regex_to_test or not site_url:
        print "Some config values or arguments not given. Exiting..."
        exit(-1)

    while True:
        print "\n", datetime.now()
        response = get_response_from_site(site_url)
        site_content = BeautifulSoup(response.text)
        page_title = site_content.find('title').text
        matching_content = site_content.find_all(text=regex_to_test)
        matching_content += site_content.find_all('a', href=regex_to_test)

        if match_if_present:
            if matching_content:
                print REGEX_FOUND_MESSAGE
                send_notification(pushbullet_api_key, page_title, site_url)
                break
            print REGEX_NOT_FOUND_MESSAGE

        else:
            if not matching_content:
                print REGEX_NOT_FOUND_MESSAGE
                send_notification(pushbullet_api_key, page_title, site_url)
                break
            print REGEX_FOUND_MESSAGE

        sleep(10)

    return


if __name__ == "__main__":
    main()
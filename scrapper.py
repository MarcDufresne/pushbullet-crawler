#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
import re
import config

from time import time, sleep
from pushbullet import PushBullet
import requests

from requests.exceptions import RequestException
from bs4 import BeautifulSoup


HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}


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


def send_notification(api_key, site_url):

    print "Sending PushBullet notification"

    pb_client = PushBullet(api_key)

    pb_client.push_link("{url} was updated!".format(url=site_url), site_url)


def main():

    config.check_config_file()
    app_config = config.load_config_file()
    pushbullet_api_key = app_config.get('api_key')
    regex_to_test = re.compile(app_config.get('regex'))
    site_url = app_config.get('site_to_parse')
    match_if_present = False if app_config.get('match_mode') == 'NOT_FOUND' else True

    start_time = time()
    interval = 10
    counter = 0

    while True:
        response = get_response_from_site(site_url)
        site_content = BeautifulSoup(response.text)
        matching_content = site_content.find_all(text=regex_to_test)
        matching_content += site_content.find_all('a', href=regex_to_test)

        if match_if_present:
            if matching_content:
                print "Regex found!"
                send_notification(pushbullet_api_key, site_url)
                break
            print "Regex not found on site"

        else:
            if not matching_content:
                print "Regex not found!"
                send_notification(pushbullet_api_key, site_url)
                break
            print "Regex found on site"

        print ""
        counter += 1
        sleep(start_time + counter * interval - time())

    return


if __name__ == "__main__":
    main()
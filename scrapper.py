#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from datetime import datetime
import re
from time import sleep

from bs4 import BeautifulSoup
from pushbullet import PushBullet
import requests
from requests.exceptions import RequestException

HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

PUSHBULLET_API_KEY = "API_KEY_HERE"


def get_response_from_site(site_url):

    site_response = None

    try:
        print "Contacting site at {url}...".format(url=site_url)
        site_response = requests.get(site_url, headers=HEADERS, timeout=30)
    except RequestException as e:
        print "Got an error trying to reach site.", e.message
        send_error_notification(content="Got an error trying to reach site.\n{}".format(e.message))
        exit(-1)

    print "Got data from site"

    return site_response


def send_error_notification(content):

    print "Got error, sending PB message"

    pb_client = PushBullet(PUSHBULLET_API_KEY)

    pb_client.push_note("Crawler Error", content)


def send_notification(detail_page_url, content=None):

    print "Sending PushBullet notification"

    pb_client = PushBullet(PUSHBULLET_API_KEY)

    if content:
        pb_client.push_link("Stock found!!", detail_page_url, body=content)
    else:
        pb_client.push_link("Stock found!", detail_page_url)


def main():

    # In stock regex
    in_stock_regex = re.compile(r'.*[Ii]n [Ss]tock.*')

    site_urls = [
        'http://www.amazon.ca/New-Nintendo-3DS-XL-Limited/dp/B00S8IGG4U/',
    ]

    while True:
        print "\n", datetime.now()
        for url in site_urls:
            response = get_response_from_site(url)
            site_content = BeautifulSoup(response.text)
            availability = site_content.find('div', id="availability_feature_div")

            print "Products availability found"

            if availability.find(text=in_stock_regex):

                product_name = site_content.find('span', id="productTitle").text

                send_notification(url, content="{} is In Stock!".format(product_name))

        sleep(300)

    return


if __name__ == "__main__":
    main()
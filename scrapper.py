#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from datetime import datetime
import re
from time import sleep
from urlparse import urlparse

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
        pb_client.push_link("MacBook found!", detail_page_url, body=content)
    else:
        pb_client.push_link("MacBook found!", detail_page_url)


def main():

    found_products_url = []

    # RAM and SSD specs regex
    ram_regex = re.compile(r'.*16[gG][bB].*')
    ssd_regex = re.compile(r'.*2[0-9]{2}[gG][bB].*')

    site_urls = [
        'http://store.apple.com/ca/browse/home/specialdeals/mac/macbook_pro',
    ]

    while True:
        print "\n", datetime.now()
        for url in site_urls:
            response = get_response_from_site(url)
            site_content = BeautifulSoup(response.text)
            products = site_content.find_all('tr', class_="product")
            domain = urlparse(url).hostname

            print "{} products found".format(len(products))

            for product in products:
                if product.find_all(text=ram_regex) and product.find_all(text=ssd_regex):
                    details_page_url = 'http://{}{}'.format(domain, product.find('a').attrs['href'])
                    if details_page_url in found_products_url:
                        print "Found already matched product"
                        continue

                    print "Match found"
                    price = product.find('span', itemprop="price").text.replace('\t', '').replace('\n', '')
                    product_specs = product.find('td', class_="specs").text.replace('\r', '')
                    product_specs = re.sub('\n{3}', ' ', product_specs)
                    product_specs = re.sub(' {2,}', ' ', product_specs)
                    product_specs = re.sub('\n ', '\n', product_specs)
                    product_specs = product_specs.strip()

                    content = "{}\n{}".format(price, product_specs)

                    send_notification(details_page_url, content=content)

                    found_products_url.append(details_page_url)

        sleep(300)

    return


if __name__ == "__main__":
    main()
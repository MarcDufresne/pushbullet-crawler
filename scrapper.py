#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
import argparse
from datetime import datetime
import re
import json

from bs4 import BeautifulSoup
from pushbullet import PushBullet
import requests
from requests.exceptions import RequestException


parser = argparse.ArgumentParser()

parser.add_argument('-r', '--region', dest='region', help='Region (us, ca, uk, etc.)', default='us')
parser.add_argument('-a', '--app', dest='game_id', help='Game ID')
parser.add_argument('-k', '--key', dest='key', help='PushBullet API Key')

args = parser.parse_args()

HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
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


def send_notification(api_key, page_title, site_url, body=None):

    print "Sending PushBullet notification"

    pb_client = PushBullet(api_key)

    pb_client.push_link("Price change for {title}!".format(title=page_title),
                        site_url, body=body)


def get_last_saved_prices():
    with open('prices.json', mode='r') as save_file:
        file_content = save_file.read()
        if not file_content:
            file_content = '{}'

    return json.loads(file_content)


def write_current_prices(prices):
    with open('prices.json', mode="w") as save_file:
        file_content = json.dumps(prices, indent=4)
        save_file.write(file_content)


def main():

    region = args.region
    game_ids = args.game_id.split(',')
    api_key = args.key

    if not api_key or not region or not game_ids:
        print "Some config values or arguments not given. Exiting..."
        exit(-1)

    current_prices = get_last_saved_prices()

    current_prices = {k: v for k, v in current_prices.items() if k in game_ids}

    for gid in game_ids:
        print "\n", datetime.now()
        site_url = "https://www.steamprices.com/{}/app/{}/".format(region, gid)

        response = get_response_from_site(site_url)
        site_content = BeautifulSoup(response.text)
        page_title = site_content.find('h1', class_="title").a.text.strip()
        text_price = site_content.find('td', class_="price_curent").span.text.strip()

        price_regex = re.compile('\d+(?:\.\d+)?')

        parsed_price = price_regex.findall(text_price)
        if parsed_price:
            price = parsed_price[0]
        else:
            price = ""

        if price != current_prices.get(gid):
            send_notification(api_key, page_title, site_url, body=text_price)
            print "New price found for {}, {}".format(page_title, text_price)
            current_prices[gid] = price
        else:
            print "Price hasn't changed, still {}".format(text_price)

    write_current_prices(current_prices)

    return


if __name__ == "__main__":
    main()

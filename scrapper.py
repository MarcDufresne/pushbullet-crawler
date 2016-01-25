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
parser.add_argument('--use-keybin', dest='use_keybin', help="Use Keybin as Data Store", action="store_true")
parser.add_argument('--keybin-host', dest='keybin_host', help="Keybin endpoint (with http, e.g. http://keybin.com/")
parser.add_argument('--user', dest='keybin_user', help="Keybin username")
parser.add_argument('--passwd', dest='keybin_pass', help="Keybin password")
parser.set_defaults(use_keybin=False)
args = parser.parse_args()

HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

KEYBIN_INFO = {
    'host': '',
    'user': '',
    'pass': ''
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


def get_keybin_token():
    keybin_resp = requests.post(
            '{}token'.format(KEYBIN_INFO['host']),
            json={'username': KEYBIN_INFO['user'],
                  'password': KEYBIN_INFO['pass'],
                  'client_id': 'steam_prices'}
    )
    try:
        keybin_resp.raise_for_status()
        full_token = keybin_resp.json()
        token = full_token.get('token', {}).get('token')
    except requests.HTTPError as e:
        print "Could not generate a token for Keybin, {}".format(e.message)
        token = None
    return token


def get_keybin_data():
    token = get_keybin_token()
    keybin_resp = requests.get(
        "{}user/{}/store/steam_prices".format(
            KEYBIN_INFO['host'], token
        )
    )
    try:
        keybin_resp.raise_for_status()
        full_store = keybin_resp.json()
        content = full_store.get('value')
    except requests.HTTPError as e:
        print "Could not read data from Keybin, {}".format(e.message)
        content = None
    return content


def write_keybin_data(data):
    token = get_keybin_token()
    keybin_resp = requests.post(
        '{}user/{}/store/steam_prices'.format(
            KEYBIN_INFO['host'], token
        ),
        json={'value': data}
    )
    try:
        keybin_resp.raise_for_status()
    except requests.HTTPError as e:
        print "Could not save data to Keybin, {}".format(e.message)


def get_last_saved_prices(use_keybin=False):
    if not use_keybin:
        with open('prices.json', mode='r') as save_file:
            content = save_file.read()
    else:
        content = get_keybin_data()

    if not content:
        content = '{}'

    return json.loads(content)


def write_current_prices(prices, use_keybin=False):
    json_prices = json.dumps(prices, indent=4)
    if not use_keybin:
        with open('prices.json', mode="w") as save_file:
            save_file.write(json_prices)
    else:
        write_keybin_data(json_prices)


def main():

    region = args.region
    game_ids = args.game_id.split(',')
    api_key = args.key

    if not api_key or not region or not game_ids:
        print "Some config values or arguments not given. Exiting..."
        exit(-1)

    use_keybin = args.use_keybin
    if use_keybin and (not args.keybin_user or not args.keybin_pass or not args.keybin_host):
        print "Keybin credentials must be set if using Keybin"
        use_keybin = False

    if use_keybin:
        KEYBIN_INFO['host'] = args.keybin_host
        KEYBIN_INFO['user'] = args.keybin_user
        KEYBIN_INFO['pass'] = args.keybin_pass

    current_prices = get_last_saved_prices(use_keybin=use_keybin)

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
            print "New price found for {}, {}".format(page_title.encode('ascii', 'ignore'), text_price)
            current_prices[gid] = price
        else:
            print "Price hasn't changed, still {}".format(text_price)

    write_current_prices(current_prices, use_keybin=use_keybin)

    return


if __name__ == "__main__":
    main()

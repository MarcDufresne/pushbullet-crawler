SteamPrice Crawler
==================

A web crawler that watches prices for games on SteamPrice.

Usage:

    ./scrapper.py -r <region> -a <game_id[,game_id,...]> -k <pushbullet_api_key>
    
    region: ca, us, uk, etc. (found in the URL on SteamPrice)
    game_id: comma separated list of numbers (e.g. 238460 or 238460,252950; found in the URL on SteamPrice)
    pushbullet_api_key: your API key for PushBullet
    
This script is intended to be used in a cron job

    0 */6 * * * /path/to/scrapper.py -r <region> -a <game_id[,game_id,...]> -k <pushbullet_api_key>

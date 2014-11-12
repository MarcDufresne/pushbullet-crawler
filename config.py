from ConfigParser import ConfigParser
import os


HOME_DIR = os.path.expanduser("~")
CONFIG_FOLDER = '/.pushbullet-crawler/'
CONFIG_FILE = '/.pushbullet-crawler/pushbullet-crawler.conf'


def check_config_file():

    if not os.path.exists(HOME_DIR + CONFIG_FOLDER):
        os.makedirs(HOME_DIR + CONFIG_FOLDER)

    config_file = HOME_DIR + CONFIG_FILE

    if not os.path.isfile(config_file):
        with open(config_file, 'w') as c_file:
            c_file.write('[Crawler]\n')
            c_file.write('API_KEY: PUSHBULLET_API_KEY_HERE\n')
            c_file.write('REGEX: (.*?)(texttomatch)(.*?)\n')
            c_file.write('MATCH_MODE: FOUND\n')
            c_file.write('# FOUND will work if the regex is present, NOT_FOUND if the regex is not present\n')
            c_file.write('SITE_TO_PARSE: http://sitetoparse.com\n')
            c_file.close()

    return config_file


def load_config_file():

    config = ConfigParser()
    config.read(HOME_DIR + CONFIG_FILE)

    sections = config.sections()

    options = []

    for section in sections:
        options.extend(config.items(section))

    configs = {}

    for option in options:
        configs[option[0]] = option[1]

    return configs
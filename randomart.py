#!/usr/bin/python

import config
import status
import logger
import random
import argparse
import sys
from time import sleep

"""uses all other modules to post tweets if chance is met, 
calls the logger and parses the CLI arguments"""


def post_tweet(text, reply_id, test=False):
    """sending tweet"""
    api = config.api
    tweet = status.Tweet()
    media,tweetxt,media_state = tweet.media(config.source_folder)
    log = config.log_file
    tolerance = config.tolerance
    already_tweeted = status.is_already_tweeted(log, media, tolerance)
    if already_tweeted or media_state == 'notart' or media_state == 'low_quality':
        if media_state != 'low_quality':
            logger.addPost(media, media_state, config.log_file)
        return post_tweet(text, reply_id)  # just try again
    if not test:
        status.tweet(media, tweetxt, reply_id, api)
        logger.addPost(media, media_state, config.log_file)
    if test:
        logger.addPost(media, "TEST", log)


def parse_args(args):
    """parsing arguments from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--tweet", help="Ignores execution chance, always run",
                        action="store_true")
    parser.add_argument("--test", help="Wont't tweet, just write to log",
                        action="store_true")
    return parser.parse_args(args)


def main():
    """runs the whole program"""
    global api  # it's used absolutely everywhere, so might as well be global
    api = config.api
    status.welcome()
    args = parse_args(sys.argv[1:])
    test = args.test
    forceTweet = args.tweet
    while True:
        if random.randint(0, 99) < config.chance or test or forceTweet:
            try:
                post_tweet(None, None, test)
            except RuntimeError:
                warning = "!CRITICAL! no non-repeated images found"
                logger.addWarning(warning, config.log_file)
            except Exception as e:
                print(e)
                print ('something fucked up, restarting bot in 60 seconds..\n\nif this happens right after start pls check if you filled settings.txt correctly\nor contact https://twitter.com/digitaImadness')
                sleep(60)
                main()
            if forceTweet:
                break
        else:
            print('sleeping for',config.interval,'s..')
        sleep(config.interval)

if __name__ == "__main__":
    main()

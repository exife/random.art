from bot import config,logger,status
from argparse import ArgumentParser
from sys import argv,exit
from time import sleep
from re import sub
import tweepy
import random

'''uses all other modules to post tweets if chance is met'''


def main():
    '''runs the whole program'''
    args = parse_args(argv[1:])
    restart = False
    global api
    auth1 = tweepy.OAuthHandler(config.api_key, config.secret_key)
    auth1.set_access_token(config.token, config.secret_token)
    if args.a:
        auth2 = tweepy.OAuthHandler(config.api_key_alt, config.secret_key_alt)
        auth2.set_access_token(config.token_alt, config.secret_token_alt)
    status.welcome()
    alt = args.a
    while True:
        try:
            if args.a and not restart:
                alt = not alt #switch accounts
            auth = auth2 if alt else auth1
            api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
            restart = post_tweet(args.g, alt)
        except Exception as eeee:
            restart = True
            print(eeee,'\n\nsomething fucked up, restarting bot in 60 sec..\n\nif it happens after start check if you filled settings.txt correctly')
            sleep(60)
            status.welcome()


def post_tweet(gif, alt):
    '''check media state and send tweet'''
    media_state = ''
    proxify = False
    characters = []
    copyright = []
    myname = api.me().screen_name
    print('\nlogged in as @' + myname)
    while media_state != 'art':
        media,artist,url,media_state,predictions,faces_detected,danbooru_id,media_log = status.media(gif, alt, proxify)
        if media_state == 'not_art':
            logger.add_post(media_log)
        elif media_state == 'api_exceeded':
            proxify = True
    if danbooru_id != 0 and media_state != 'anime':
        post = status.danbooru(danbooru_id)
        if post != '':
            '''if (alt and post['rating'] == 's') or (not alt and post['rating'] == 'e'):
                print('rating is unacceptable:',post['rating'],'trying another pic..')
                logger.add_post(media_log)
                return True'''
            copyright = post['tag_string_copyright'].split()
            characters = post['tag_string_character'].split()
            if copyright != []:
                copyright = ['{0}'.format(sub(r'\([^)]*\)', '', tag)) for tag in copyright] #remove (anime_name) from character name
                if copyright[0] != 'original' and characters != []:
                    characters = ['{0}'.format(sub(r'\([^)]*\)', '', tag)) for tag in characters] 
                copyright = ['{0}'.format(tag.replace('_', ' ')) for tag in copyright]
                copyright = ['{0}'.format(tag.strip()) for tag in copyright]
            if characters != []:
                characters = ['{0}'.format(tag.replace('_', ' ')) for tag in characters]
                characters = set(['{0}'.format(tag.strip()) for tag in characters])
            duplicate_characters = set([])
            for tag in characters:
                if next((True for tag2 in characters if tag in tag2 and tag != tag2), False): #search incomplete tags
                    duplicate_characters.add(tag)
            characters = set(characters) - duplicate_characters
            if len(characters) < 5:
                tweetxt = ', '.join(characters)
                if copyright != [] and copyright[0] != 'original':
                    tweetxt += ' (' + copyright[0] + ')'
            elif copyright != [] and copyright[0] != 'original':
                tweetxt = copyright[0]
    elif config.neural_opt and faces_detected:
        waifus = ''
        for waifu in predictions:
            if waifu[1] >= 0.9:
                waifus += waifu[0] + ' (' + str(int(waifu[1]*100)) + '%) '
        if waifus != '':
            tweetxt += '\n' + waifus
    if artist == '':
        artist = post['tag_string_artist']
        artist.replace('_', ' ')
        artist.strip()
    if artist != '':
        status.tweet(media, tweetxt + ' by ' + artist, api, myname)
    else:
        status.tweet(media, tweetxt, api, myname)
    logger.add_post(media_log)
    print('ok! sleeping for',config.interval,'s before next tweet..')
    sleep(config.interval)


def parse_args(args):
    '''parse CLI arguments'''
    parser = ArgumentParser()
    parser.add_argument('-a', help='multiaccount', action='store_true')
    parser.add_argument('-g', help='tweet gifs only', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    main()

#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy, time, sys, json, creds
from urlparse import urlparse, urlunparse
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from logger import logger_setup

log = logger_setup('mirroronimgur-bot')

class MirrorOnImgurBot(tweepy.StreamListener):

    def __init__(self):
        # bot twitter user name
        self.username = 'mirroronimgur' # change to mirroronimgur

        self.auth_twitter()
        self.auth_imgur()

        log.info('Init done')

    def auth_twitter(self):
        """ Authenticate with twitter and setup the 'api' object """

        log.info('Wiring up twitter auth')
        # wire up stuff with twitter auth
        self.auth = tweepy.OAuthHandler(creds.T_CONSUMER_KEY, creds.T_CONSUMER_SECRET)
        self.auth.set_access_token(creds.T_ACCESS_TOKEN, creds.T_ACCESS_TOKEN_SECRET)
        self.api  = tweepy.API(self.auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

    def auth_imgur(self):
        """ Authenticate with imgur and setup the imgur client """

        log.info('Wiring up imgur auth')
        # wire up stuff with imgur auth
        self.imgur_client = ImgurClient(creds.I_CLIENT_ID, creds.I_CLIENT_SECRET)

    def rate_limit_status(self):
        """ Print twitter rate limit status """

        log.info('Rate limit status:\n%r' % self.api.rate_limit_status())

    def on_error(self, status):
        """ Handle twitter streaming endpoint error """

        log.error('Error: %r' % status)
        self.rate_limit_status()

    def on_data(self, raw_data):
        """ Handle tweets received from the twitter streaming endpoint.
        This method is pretty much the whole bot. It parses the tweet, pulls out the url, uploads
        to imgur and replies to the tweet it had received with the new imgur url
        """

        data             = json.loads(raw_data)
        user_mentions    = data.get('entities', {}).get('user_mentions', [])
        sender_username  = data.get('user', {}).get('screen_name', 'UnknownUser')
        bot_is_mentioned = len(filter(lambda mentioned_user : mentioned_user['screen_name'] == self.username, user_mentions)) > 0

        log.debug('Data %r' % data)
        log.info('Message from: %r' % sender_username)
        log.info('Is the bot mentioned? %r' % bot_is_mentioned)

        # print "is the bot mentioned? %r" % bot_is_mentioned
        # if it's not a retweet and it isn't a tweet to myself from my own account
        # and if bot is mentioned then do stuff
        if not data['retweeted'] and sender_username != self.username and bot_is_mentioned:
            try:
                tweet_id = data.get('id_str')
                url  = 'http' + data.get('text', '').split('http')[1].strip().split()[0].strip()
            except Exception as e:
                log.error('Error: %r', e)
            finally:
                url = ''
                self.handle_msg(url, tweet_id, sender_username)

    def handle_msg(self, url, tweet_id, sender_username):
        """ Decide what to do based on url
        If it's valid, upload to imgur else reply with an error message
        """

        log.info('Url received: %r' % url)

        parsedUrl = urlparse(url)

        # if the url is indeed valid (has a hostname)
        if parsedUrl.netloc != '':
            imgur_reply = self.imgur_client.upload_from_url(url)
            msg         = '@' + sender_username + ' ' + imgur_reply.get('link', 'Upload failed')
            log.debug('Imgur response: %r' % imgur_reply)
            log.info('Bot reply: %r to tweet id %r' % (msg, tweet_id))
            self.api.update_status(status = msg, in_reply_to_status_id = tweet_id)
        else:
            self.api.update_status(status = 'Send me a valid url please :)', in_reply_to_status_id = tweet_id)

        log.info('Reply sent')

if __name__ == '__main__':
    bot = MirrorOnImgurBot()
    stream = tweepy.Stream(auth = bot.auth, listener = bot)
    stream.filter(track=[bot.username])

#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy, json
from urlparse import urlparse, urlunparse
from logger import logger_setup
from twitterAuth import TwitterAuth
from imgurAuth import ImgurAuth

log = logger_setup('mirroronimgur-bot')

class MirrorOnImgurBot(tweepy.StreamListener):

    def __init__(self):
        # bot twitter user name
        self.username = 'mirroronimgur'

        self.twitter = TwitterAuth()
        self.imgur = ImgurAuth()

        log.info('Init done')

    def on_error(self, status):
        """ Handle twitter streaming endpoint error """

        log.error('Error: %r' % status)
        self.twitter.rate_limit_status()

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

        # if it's not a retweet and it isn't a tweet to myself from my own account
        # and if bot is mentioned then do stuff
        if not data['retweeted'] and sender_username != self.username and bot_is_mentioned:
            try:
                tweet_id = data.get('id_str')
                url  = 'http' + data.get('text', '').split('http')[1].strip().split()[0].strip()

            except Exception as e:
                log.error('Error: %r', e)
                url = ''

            finally:
                self.handle_url(url, tweet_id, sender_username)

    def handle_url(self, url, tweet_id, sender_username):
        """ Decide what to do based on url

        If it's valid, upload to imgur else reply with an error message
        """

        sender_username = '@' + sender_username

        log.info('Url received: %r' % url)
        log.info('Reply to user: %r' % sender_username)

        try:
            parsedUrl = urlparse(url)

            # if the url is indeed valid (has a hostname)
            if parsedUrl.netloc != '':
                # mirror on imgur
                imgur_reply = self.imgur.client.upload_from_url(url)
                msg         = sender_username + ' ' + imgur_reply.get('link', 'Upload failed')

                log.debug('Imgur response: %r' % imgur_reply)
                log.info('Bot reply: %r to tweet id %r' % (msg, tweet_id))

                self.twitter.client.update_status(status = msg, in_reply_to_status_id = tweet_id)
            else:
                self.twitter.client.update_status(status = sender_username + ' ' + 'send me a valid url please :)', in_reply_to_status_id = tweet_id)

        except Exception as e:
            log.error('Error: %r' % e)
            self.twitter.client.update_status(status = sender_username + ' ' + 'something went wrong. womp womp :(', in_reply_to_status_id = tweet_id)

        finally:
            log.info('Reply sent')

if __name__ == '__main__':
    bot = MirrorOnImgurBot()
    stream = tweepy.Stream(auth = bot.twitter.auth, listener = bot)
    stream.filter(track=[bot.username])

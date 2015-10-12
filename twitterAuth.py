import tweepy, creds

log = logger_setup('twitterauth')

class TwitterAuth:

    def __init__(self):
        """ Authenticate with twitter and setup the 'api' object """

        log.info('Wiring up twitter auth')
        # wire up stuff with twitter auth
        self.auth = tweepy.OAuthHandler(creds.T_CONSUMER_KEY, creds.T_CONSUMER_SECRET)
        self.auth.set_access_token(creds.T_ACCESS_TOKEN, creds.T_ACCESS_TOKEN_SECRET)
        self.client  = tweepy.API(self.auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

    def rate_limit_status(self):
        """ Print twitter rate limit status """

        log.info('Rate limit status:\n%r' % self.client.rate_limit_status())

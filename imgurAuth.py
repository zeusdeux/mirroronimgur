import creds
from imgurpython import ImgurClient

log = logger_setup('imgurauth')

class ImgurAuth:

    def __init__(self):
        """ Authenticate with imgur and setup the imgur client """

        log.info('Wiring up imgur auth')
        # wire up stuff with imgur auth
        self.client = ImgurClient(creds.I_CLIENT_ID, creds.I_CLIENT_SECRET)

import requests
import re
import urllib
import json

HTTPRegexp = "/^http:\/\//"
defaultApiURL = "/.netlify/identity"


class Client:
    def __init__(self, url, audience='', setCookie=False):
        if re.match(HTTPRegexp, url):
            # TODO: Decide whether to convert this to a logging statement
            print(
                "Warning:\n\nDO NOT USE HTTP IN PRODUCTION FOR GOTRUE EVER!\nGoTrue REQUIRES HTTPS to work securely."
            )

        self.BASE_URL = url

    def _request(path, options=[]):
        options = option.headers or []
        aud = options.audience or self.audience
        if aud:
            options.headers['X-JWT-AUD'] = aud

    def settings(self):
        r = requests.get(f"{self.BASE_URL}/settings")
        return r

    def sign_up(credentials):
        data = json.dumps({
            "email": "yadayada@gmail.com",
            "password": "yadayada"
        })
        requests.post(f"{self.BASE_URL}/signup", data)

    def login():
        pass

    def login_external_url(provider):
        pass

    def confirm(token, remember):
        pass

    def request_password_recovery(email):
        pass

    def recover(token, remember):
        """ Send a recovery email """
        pass

    def accept_invite(token, password, remember):
        pass

    def acceptInviteUrl(provider, token):
        pass

    def get_user():
        pass

    def update_user():
        pass

    def verify(type, token, remember):
        requests.post(f"{self.BASE_URL}/verify",
                      data=json.dumps({
                          "type": "signup",
                          "token": "cixoe6C7k1tqx2UuYL_O3w"
                      }))

    def send_magic_link(self, email: str):
        """Send a magic link for passwordless login"""
        data = json.dumps({"email": email})
        return requests.post(f"{self.BASE_URL}/magiclink", data=data)

    def grant_token(type, payload):
        payload = json.dumps({
            "email": "yadayada@gmail.com",
            "password": "yadayada"
        })
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        requests.post(
            "https://distracted-elion-6bf6a2.netlify.app/.netlify/identity/verify",
            data=json.dumps({
                "type": "signup",
                "token": "tokenthing"
            }))

import requests
import re
import urllib
import json

HTTPRegexp = "/^http://"
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

    def sign_up(credentials: dict):
        requests.post(f"{self.BASE_URL}/signup", credentials)

    def login():
        pass

    def login_external_url(provider):
        pass

    def logout(jwt: str):
        # TODO: Validate how to send jwt
        requests.post(f"{self.BASE_URL}/logout", jwt)

    def confirm(self, token, remember):
        pass

    def recover(self, email: str):
        """ Send a recovery email """
        data = json.dumps({"email": email})
        return requests.post(f"{self.BASE_URL}/recover", data)

    def accept_invite(self, token, password, remember):
        pass

    def get_user():
        requests.get(f"{self.BASE_URL}/user", jwt)

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

    def invite(self, invitation):
        """Invite a new user to join"""
        return requests.post(f"{self.BASE_URL}/invite", invitation)

    def grant_token(type, payload):
        payload = json.dumps({
            "email": "yadayada@gmail.com",
            "password": "yadayada"
        })
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        requests.post(f"{self.BASE_URL}/verify",
                      data=json.dumps({
                          "type": "signup",
                          "token": "tokenthing"
                      }))

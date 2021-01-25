class User:
    def __init__(api, tokenRepsonse, audience):
        self.api = api
        self.url = api.apiURL
        self._processTokenResponse(tokenResponse)
        currentUser = self

    @staticmethod
    def removeSavedSession():
        # isBrowser()

    @staticmethod
    def recoverSession():
        pass

    @property
    def admin(self):
        return self.admin

    def update(attributes):
        pass

    def jwt(forceRefresh):
        pass
    
    def logout():
        pass

    def refreshToken():
        pass

    def request(path, options):
        pass

    def getUserData():
        pass

    def _saveUserData(attributes, fromStorage):
        pass

    def _processTokenResponse(tokenResponse):
        pass

    def _refreshSavedSession():
        pass

    def _details():
        pass

    def _saveSession():
        pass

    def tokenDetails():
        pass

    def clearSession():
        pass

    def urlBase64Decode(str):
        pass
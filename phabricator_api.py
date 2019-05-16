import requests


class Phabricator:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def phid_query(self, phid):
        data = {
            'api.token': self.token,
            'phids[0]': phid
        }

        response = requests.post(self.base_url + '/api/phid.query', data=data)
        return response.json()

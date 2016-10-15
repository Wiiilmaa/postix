import json
import logging

import requests

from c6sh.core.models.settings import EventSettings


class OverheadPrinter:
    def __init__(self, ip_address, *args, **kwargs):
        self.ip_address = ip_address

    def _request(self, method):
        payload = {
            'method': method,
            'id': 1
        }
        headers = {'Content-Type': 'application/json'}
        url = 'http://{}:8888/jsonrpc'.format(self.ip_address)
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            timeout=0.5,
        )
        return r.json().get('result', r.json().get('error'))

    def open(self):
        return self._request('open')

    def next(self):
        return self._request('next')


class DummyPrinter:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('django')

    def open(self):
        self.logger.info('[DummyDisplay] Cashdesk was opened')

    def next(self):
        self.logger.info('[DummyDisplay] Cashdesk is ready for next transaction')

import requests, json
from datetime import datetime, timedelta

class RequestCache:
    def __init__(self, cache_time=300):
        self.cache_time = cache_time
        self.cache_data = []

    def get(self, method, uri, payload, headers):
        for entry in self.cache_data:
            if method in entry['method'] and uri in entry['uri'] and payload in entry['payload']:
                return entry['response']
        return None

    def clear(self):
        self.cache_data = []

    def request(self, method, uri, payload, headers):
        cache = self.get(method, uri, payload, headers)
        if cache is not None and cache['expiry'] < datetime.now():
            return cache['response']
        response = requests.request(method, uri, data=payload, headers=headers)
        json_response = json.loads(response.text)
        self.cache_data.append({
            'method': method,
            'uri': uri,
            'payload': payload,
            'headers': headers,
            'response': json_response,
            'expiry': datetime.now() + timedelta(seconds=self.cache_time)
        })
        return json_response
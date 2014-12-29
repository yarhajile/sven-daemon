import requests
import Sven.Exception
import logging
import simplejson as json

from Sven.Methods import *

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

class Requests(object):
  def headers(self, extraHeaders = None):
    headers = {}

    if extraHeaders is not None:
      headers.update(extraHeaders)

    return headers


  def post(self, url, data = None, headers = None):
    return self._request('post', url, data, headers)


  def get(self, url, data = None, headers = None):
    return self._request('get', url, data, headers)


  def put(self, url, data = None, headers = None):
    return self._request('put', url, data, headers)


  def delete(self, url, data = None, headers = None):
    return self._request('delete', url, data, headers)


  def _request(self, method, url, data = None, headers = None):
    notice('===================')
    notice('Method: ' + method)
    notice('URL: ' + url)
    notice(data)
    notice(self.headers(headers))
    notice('===================')

    if method == 'post':
      response = requests.post(url, headers = self.headers(headers),data = data)

    if method == 'get':
      response = requests.get(url, headers = self.headers(headers), data = data)

    if method == 'put':
      response = requests.put(url, headers = self.headers(headers), data = data)

    if method == 'delete':
      response = requests.delete(url, headers = self.headers(headers),
                                 data = data)

    if response.status_code == 401:
      response.raise_for_status()

    try:
      response.json()
    except:
      response.raise_for_status()

    return response

# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import threading


class tinify():
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if not tinify.__instance:
            tinify()
        return tinify.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if tinify.__instance:
            raise Exception("This class is a singleton!")
        else:
            self._lock = threading.RLock()

            self._client = None
            self._key = None
            self._app_identifier = None
            self._proxy = None
            self._compression_count = None
            tinify.__instance = self

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value
        self._client = None

    @property
    def app_identifier(self):
        return self._app_identifier

    @app_identifier.setter
    def app_identifier(self, value):
        self._app_identifier = value
        self._client = None

    @property
    def proxy(self):
        return self._key

    @proxy.setter
    def proxy(self, value):
        self._proxy = value
        self._client = None

    @property
    def compression_count(self):
        return self._compression_count

    @compression_count.setter
    def compression_count(self, value):
        self._compression_count = value

    def get_client(self):
        if not self._key:
            raise AccountError('Provide an API key with tinify.key = ...')

        if not self._client:
            with self._lock:
                if not self._client:
                    self._client = Client(self._key, self._app_identifier, self._proxy)

        return self._client

    def validate(self):
        try:
            self.get_client().request('post', '/shrink')
        except AccountError as err:
            if err.status == 429:
                return True
            raise err
        except ClientError:
            return True

    def from_file(self, path):
        return Source.from_file(path)

    def from_buffer(self, string):
        return Source.from_buffer(string)

    def from_url(self, url):
        return Source.from_url(url)

from .version import __version__

from .client import Client
from .result_meta import ResultMeta
from .result import Result
from .source import Source
from .errors import *

__all__ = [
    b'Client',
    b'Result',
    b'ResultMeta',
    b'Source',
    b'Error',
    b'AccountError',
    b'ClientError',
    b'ServerError',
    b'ConnectionError'
]

from inflection import underscore, pluralize, singularize
import pandas as pd
import requests

from .version import VERSION
from .utils import merge_to_dicts

class Config(object):
    """Configuracao."""
    api_key = None
    base_dev_url = 'https://dev.labmet.com.br'
    base_prod_url = 'https://api.labmet.com.br'
    version = 'v1'
    mode = 'dev'


class LabMetError(RuntimeError):
    """
    LabMet Error
    """
    DEFAULT_MSG = 'Something went wrong. Please contact us at contato@labmet.com.br.'

    def __init__(self, labmet_message=None, http_status=None, http_body=None, http_headers=None,
                 labmet_error_code=None, response_data=None):
        self.http_status = http_status
        self.http_body = http_body
        self.http_headers = http_headers if http_headers is not None else {}

        self.labmet_error_code = labmet_error_code
        self.labmet_message = labmet_message if labmet_message is not None \
            else self.DEFAULT_MSG
        self.response_data = response_data

    def __str__(self):
        if self.http_status is None:
            status_string = ''
        else:
            status_string = "(Status %(http_status)s) " % {"http_status": self.http_status}
        if self.labmet_error_code is None:
            labmet_error_string = ''
        else:
            labmet_error_string = "(LabMet Error %(labmet_error_code)s) " % {
                "labmet_error_code": self.labmet_error_code}
        return "%(ss)s%(qes)s%(qm)s" % {
            "ss": status_string, "qes": labmet_error_string, "qm": self.labmet_message
        }


class InvalidRequest(LabMetError):
    pass

class Connection:
    """Api Connection."""

    @classmethod
    def request(cls, method, url, **options):
        if 'headers' in options:
            headers = options['headers']
        else:
            headers = {}

        accept_value = 'application/json'

        headers = merge_to_dicts({'accept': accept_value,
                                  'request-source': 'python',
                                  'request-source-version': VERSION}, headers)
        if Config.api_key:
            headers = merge_to_dicts({'x-api-key': Config.api_key}, headers)

        options['headers'] = headers
        
        if Config.mode == 'dev':
            base_url = Config.base_dev_url
        else:
            base_url = Config.base_prod_url
        
        _url = '%s/%s/%s' % (base_url, Config.version, url)

        return cls.execute_req(method, _url, **options)

    @classmethod
    def execute_req(cls, method, url, **options):
        try:
            func = getattr(requests, method)
            response = func(url, **options)
            if response.status_code < 200 or response.status_code >= 300:
                # Parse errors
                cls.handle_error(response)
            else:
                return response
        except requests.exceptions.RequestException as e:
            if e.response:
                cls.handle_error(e.response)
            raise e

    @classmethod
    def parse(cls, response):
        try:
            return response.json()
        except ValueError:
            raise LabMetError(http_status=response.status_code, http_body=response.text)

    @classmethod
    def handle_error(cls, resp):
        error_body = cls.parse(resp)

        if 'labmet_error' not in error_body:
            raise LabMetError(http_status=resp.status_code, http_body=resp.text)

        code = error_body['labmet_error']['code']
        message = error_body['labmet_error']['message']
        raise LabMetError(message, resp.status_code, resp.text, resp.headers, code)



class Rain(object):
    @classmethod
    def get_path(cls):
        return underscore(pluralize(cls.__name__))
    
    @classmethod
    def parse(cls, data):
        _data = pd.DataFrame(data)
        if 'date' in _data.columns:
            _data['date'] = pd.to_datetime(_data['date'], format='%Y-%m-%d')
            _data.set_index('date', inplace=True)
        return _data
    
    @classmethod
    def get_data(cls, **options):
        r = Connection.request('get', cls.get_path(), **options)
        response_data = r.json()
        return cls.parse(response_data[cls.get_path()])



def get(model, **options):
    """Return dataframe of requested dataset from Labmet.
    :param model: str 
    :param str start, end: required datefilers
    :param float or str lat, lng: required position filters
    :param str group: group data are daily, weekly, monthly, quarterly, annual
    :param str transform: options are diff, rdiff, cumul, and normalize
    :returns: :class:`pandas.DataFrame` or :class:`numpy.ndarray`
    Any other `kwargs` passed to `get` are sent as field/value params to Labmet
    with no interference
    """

    # Por enquanto o modulo é sempre rain.
    params = {'params': options}
    return Rain.get_data(**params)

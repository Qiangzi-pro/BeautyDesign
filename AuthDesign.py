from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta


class AuthToken(object):
    DEFAULT_EXPIRED_TIME_INTERVAL = timedelta(seconds=1*60*1000)

    def __init__(self, token, create_time, expired_time_interval=DEFAULT_EXPIRED_TIME_INTERVAL):
        self.token = token
        self.create_time = create_time
        self.expired_time_interval = expired_time_interval

    @staticmethod
    def create(base_url, create_time, params: map):
        param_str = '&'.join(['%s=%s' % (name, value) for name, value in params.items])
        pass

    def get_token(self):
        return self.token

    def is_expired(self):
        return datetime.now() > (self.create_time + self.expired_time_interval)

    def match(self, auth_token):
        return self.token ==  auth_token.token


class ApiRequest(object):
    def __init__(self, baseUrl, token, appId, timestamp: int):
        self.base_url = baseUrl
        self.token = token
        self.app_id = appId
        self.timestamp = timestamp

    @staticmethod
    def create_from_full_url(url):
        mark_idx = url.index('?')
        url_segment = url[mark_idx + 1:].split('&')
        param_map = {}
        for param_pair in url_segment:
            name, value = param_pair.split('=')
            param_map[name] = value

        return ApiRequest(**param_map)

    def get_base_url(self):
        return self.base_url

    def get_token(self):
        return self.token

    def get_app_id(self):
        return self.app_id

    def get_timestamp(self):
        return self.timestamp


class CredentialStorage(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_password_by_app_id(cls, app_id):
        pass


class ApiAuthenticator(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def auth(cls, api_request):
        pass


class DefaultApiAuthenticatorImpl(ApiAuthenticator):
    def __init__(self, credential_storage=None):
        self.credential_storage = credential_storage

    @classmethod
    def auth(cls, api_request):
        if isinstance(api_request, str):
            pass
        elif isinstance(api_request, ApiRequest):
            pass
        else:
            raise ValueError('参数类型错误')

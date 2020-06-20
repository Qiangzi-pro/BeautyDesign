from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
import hashlib


# 接口定义

class CredentialStorage(metaclass=ABCMeta):
    """
    秘钥存储接口
    """

    @abstractmethod
    def get_password_by_app_id(self, app_id):
        pass


class ApiAuthenticator(metaclass=ABCMeta):
    """
    API鉴权认证器接口
    """

    @abstractmethod
    def auth(self, api_request):
        pass


# URL通用函数
def get_alpha_query_param_str(params: dict):
    params_list = sorted(params.items())
    param_str = '&'.join(['%s=%s' % (name, value) for name, value in params_list])
    return param_str


def get_integral_url(base_url, params):
    if isinstance(params, dict):
        param_str = get_alpha_query_param_str(params)
    elif isinstance(params, str):
        param_str = params
    else:
        raise TypeError('error params')

    integral_url = base_url
    if base_url[-1] != '?':
        integral_url += '?'
    integral_url += param_str

    return integral_url


# 具体类
class AuthToken(object):
    """
    鉴权TOKEN类，负责处理token相关操作，包括生成token, 超期检查，鉴权比较
    """
    DEFAULT_EXPIRED_TIME_INTERVAL = timedelta(seconds=1*60*1000)

    def __init__(self, token, timestamp, expired_time_interval=DEFAULT_EXPIRED_TIME_INTERVAL):
        self.token = token
        self.timestamp = timestamp  # 创建时间戳
        self.expired_time_interval = expired_time_interval

    @classmethod
    def generate_token(cls, url):
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    @staticmethod
    def create(base_url, **params):
        integral_url = get_integral_url(base_url, params)
        token = AuthToken.generate_token(integral_url)

        return AuthToken(token, params['timestamp'])

    def get_token(self):
        return self.token

    def is_expired(self):
        return datetime.now() > (datetime.fromtimestamp(self.timestamp) + self.expired_time_interval)

    def match(self, auth_token):
        return self.token == auth_token.token


class ApiRequest(object):
    """
    请求REQUEST类，负责转化一个request为基本的数据结构
    """
    def __init__(self, baseUrl, token, app_id, timestamp):
        self.base_url = baseUrl
        self.token = token
        self.app_id = app_id
        self.timestamp = int(timestamp)

    @property
    def integral_url(self):
        import copy
        data = copy.copy(self.__dict__)
        data.pop('base_url')

        return get_integral_url(self.base_url, data)

    @staticmethod
    def build_from_integral_url(url):
        mark_idx = url.index('?')
        url_segment = url[mark_idx + 1:].split('&')
        param_map = {}
        for param_pair in url_segment:
            name, value = param_pair.split('=')
            param_map[name] = value

        return ApiRequest(baseUrl=url[:mark_idx], **param_map)

    def get_base_url(self):
        return self.base_url

    def get_token(self):
        return self.token

    def get_app_id(self):
        return self.app_id

    def get_timestamp(self):
        return self.timestamp


class DefaultCredentialStorageImpl(CredentialStorage):
    def get_password_by_app_id(self, app_id):
        return int(app_id) + 2020


class DefaultApiAuthenticatorImpl(ApiAuthenticator):
    def __init__(self, credential_storage=None):
        if credential_storage is None:
            credential_storage = DefaultCredentialStorageImpl()
        self._credential_storage = credential_storage

    def auth(self, raw_request):
        if isinstance(raw_request, str):
            api_request = ApiRequest.build_from_integral_url(raw_request)
        else:
            api_request = raw_request

        if not isinstance(api_request, ApiRequest):
            raise ValueError('参数类型错误')

        app_id = api_request.app_id
        token = api_request.token
        timestamp = api_request.timestamp
        base_url = api_request.base_url

        client_auth_token = AuthToken(token, timestamp)

        if client_auth_token.is_expired():
            raise RuntimeError('Token is expired')

        password = self._credential_storage.get_password_by_app_id(app_id)
        server_auth_token = AuthToken.create(
            base_url=base_url,
            app_id=app_id,
            password=password,
            timestamp=timestamp,
        )

        return server_auth_token.match(client_auth_token)


if __name__ == '__main__':
    authenticator = DefaultApiAuthenticatorImpl()
    credential_storage = DefaultCredentialStorageImpl()

    app_id = 1128
    timestamp = int((datetime.now() - timedelta(hours=3)).timestamp())

    params = {
        'app_id': app_id,
        'password': credential_storage.get_password_by_app_id(app_id),
        'timestamp': timestamp,
    }

    baseUrl = 'https://time.geekbang.org/column/article/171767'
    auth_token = AuthToken.create(baseUrl, **params)

    api_request = ApiRequest(baseUrl, auth_token.token, app_id, timestamp)

    print(authenticator.auth(api_request.integral_url))

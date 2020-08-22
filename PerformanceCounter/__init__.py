
class RequestInfo(object):
    """
    api请求info类
    """
    def __init__(self, api_name: str, response_time: int, timestamp: int):
        self._api_name = api_name
        self._response_time = response_time
        self._timestamp = timestamp

    @property
    def api_name(self):
        return self._api_name

    @property
    def response_time(self):
        return self._response_time


class RequestStat(object):
    def __init__(self, max_response_time, min_response_time, avg_response_time,
                 p999_response_time, p99_response_time,
                 count, tps):
        self.max_response_time = max_response_time
        self.min_response_time = min_response_time
        self.avg_response_time = avg_response_time
        self.p999_response_time = p999_response_time
        self.p99_response_time = p99_response_time
        self.count = count
        self.tps = tps

"""
负责提供API， 来采集接口请求的原始数据
"""
from PerformanceCounter import RequestInfo
from PerformanceCounter.MetricsStorage import MetricsStorage


class MetricsCollector(object):

    # 依赖注入
    def __init__(self, metrics_storage: MetricsStorage):
        self._metrics_storage = metrics_storage  # 基于接口而非实现编程

    def record_request(self, request_info: RequestInfo) -> None:
        if request_info is None or request_info.api_name == '':
            return
        self._metrics_storage.save_request_info(request_info)

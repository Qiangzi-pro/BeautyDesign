"""
负责提供API， 来采集接口请求的原始数据
"""
from PerformanceCounter import RequestInfo
from PerformanceCounter.article40.MetricsStorage import MetricsStorage, RedisMetricsStorage


class EventBus(object):
    def register(self, listener):
        pass

    def post(self, info):
        pass


class MetricsCollector(object):
    DEFAULT_STORAGE_THREAD_POOL_SIZE = 20

    # 依赖注入
    def __init__(self, metrics_storage: MetricsStorage = None):
        self.metrics_storage = metrics_storage or RedisMetricsStorage()  # 基于接口而非实现编程
        self.event_bus = EventBus()  # new AsyncEventBus(Executors.newFixedThreadPool(threadNumToSaveData));
        self.event_bus.register(MetricsCollector.EventListener(self))

    def record_request(self, request_info: RequestInfo) -> None:
        """
        非功能性需求完善
        异步提交
        :param request_info:
        :return:
        """
        if request_info is None or request_info.api_name == '':
            return
        # self.metrics_storage.save_request_info(request_info)
        self.event_bus.post(request_info)

    class EventListener(object):
        def __init__(self, collector):
            self.outer_collector = collector

        def save_request_info(self, request_info):
            self.outer_collector.metrics_storage.save_request_info(request_info)

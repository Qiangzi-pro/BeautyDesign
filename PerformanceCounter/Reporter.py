"""
负责展示 OR 以一定频率统计&推送统计数据
"""
import json
import sched, time
from typing import Dict, List
from PerformanceCounter import RequestInfo, RequestStat
from PerformanceCounter.MetricsStorage import MetricsStorage
from PerformanceCounter.Aggregator import Aggregator


class ConsoleReporter(object):
    def __init__(self, metrics_storage: MetricsStorage):
        self._metrics_storage = metrics_storage
        self._executor = sched.scheduler(time.time, time.sleep)

    def start_repeated_report(self, period_in_seconds: int, duration_in_seconds: int):
        def action(*argument, **kwargs):
            # 1. 根据给定的时间区间，从数据库中拉取数据
            duration_in_millis = duration_in_seconds * 1000
            end_time_in_millis = int(time.time() * 1000)
            start_time_in_millis = end_time_in_millis - duration_in_millis
            request_infos: Dict[str, List[RequestInfo]] = self._metrics_storage.get_request_infos(start_time_in_millis, end_time_in_millis)
            stats: Dict[str, RequestStat] = dict()
            for api_name, request_infos_per_api in request_infos.items():
                # 2. 根据原始数据，计算得到统计数据
                request_stat = Aggregator.aggregate(request_infos_per_api, duration_in_millis)
                stats[api_name] = request_stat

            # 3. 将统计数据显示到终端
            print('Time Span: [{}, {}]'.format(start_time_in_millis, end_time_in_millis))
            print(stats)

        self._executor.enter(period_in_seconds, 1, action)


class EmailReporter(object):
    pass
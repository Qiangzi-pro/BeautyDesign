"""
负责根据原始数据计算统计数据
"""
import sys
from typing import List, Dict
from PerformanceCounter import RequestInfo, RequestStat


class Aggregator(object):
    def aggregate(self, request_infos: Dict[str, List[RequestInfo]], duration_in_millis: int) -> Dict[str, RequestStat]:
        request_stats = dict()
        for api_name, request_infos_per_api in request_infos.items():
            request_stat: RequestStat = self.do_aggregate(request_infos_per_api, duration_in_millis)
            request_stats[api_name] = request_stat

        return request_stats

    def do_aggregate(self, request_infos: List[RequestInfo], duration_in_millis) -> RequestStat:
        resp_times = list()
        for request_info in request_infos:
            resp_time = request_info.response_time
            resp_times.append(resp_time)

        request_stat = RequestStat(
            max_response_time=Aggregator.__max(resp_times),
            min_response_time=Aggregator.__min(resp_times),
            avg_response_time=Aggregator.__avg(resp_times),
            p999_response_time=Aggregator.__percentile999(resp_times),
            p99_response_time=Aggregator.__percentile99(resp_times),
            count=len(resp_times),
            tps=Aggregator.__tps(len(resp_times), duration_in_millis)
        )

        return request_stat

    @staticmethod
    def __max(dataset: List[float]):
        return max(dataset)

    @staticmethod
    def __min(dataset: List[float]):
        return min(dataset)

    @staticmethod
    def __avg(dataset: List[float]):
        return 1.0 * sum(dataset) / len(dataset)

    @staticmethod
    def __tps(count: int, duration_in_millis: float):
        return count / duration_in_millis * 1000

    @staticmethod
    def __percentile999(dataset: List[float]):
        sorted_dataset = sorted(dataset)
        idx = int(len(dataset) * 0.999)
        return sorted_dataset[idx]

    @staticmethod
    def __percentile99(dataset: List[float]):
        pass



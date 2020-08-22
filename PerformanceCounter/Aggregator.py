"""
负责根据原始数据计算统计数据
"""
import sys
from typing import List
from PerformanceCounter import RequestInfo, RequestStat


class Aggregator(object):
    """
    工具类？！
    """
    @staticmethod
    def aggregate(request_infos: List[RequestInfo], duration_in_millis: int) -> RequestStat:
        max_resp_time = sys.float_info.min
        min_resp_time = sys.float_info.max
        avg_resp_time = -1
        p999_resp_time = -1
        p99_resp_time = -1
        sum_resp_time = 0
        count = 0
        for request_info in request_infos:
            count += 1
            resp_time = request_info.response_time
            if max_resp_time < resp_time:
                max_resp_time = resp_time
            if min_resp_time > resp_time:
                min_resp_time = resp_time
            sum_resp_time += resp_time

        if count != 0:
            avg_resp_time = sum_resp_time * 1.0 / count
        tps = int(count * 1.0 / duration_in_millis * 1000)
        request_infos.sort(key=lambda item: item.response_time)
        idx999 = int(count * 0.999)
        idx99 = int(count * 0.99)
        if count != 0:
            p999_resp_time = request_infos[idx999].response_time
            p99_resp_time = request_infos[idx99].response_time

        request_stat = RequestStat(
            max_response_time=max_resp_time,
            min_response_time=min_resp_time,
            avg_response_time=avg_resp_time,
            p999_response_time=p999_resp_time,
            p99_response_time=p99_resp_time,
            count=count,
            tps=tps
        )

        return request_stat

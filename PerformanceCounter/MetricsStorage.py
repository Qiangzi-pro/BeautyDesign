"""
负责原始数据的存储
"""
from abc import ABCMeta, abstractmethod
from typing import List, Dict
from PerformanceCounter import RequestInfo


class MetricsStorage(metaclass=ABCMeta):
    @abstractmethod
    def save_request_info(self, request_info: RequestInfo) -> None:
        pass

    @abstractmethod
    def get_request_infos_by_api(self, api_name, start_time_in_millis, end_time_in_millis) -> List[RequestInfo]:
        pass

    @abstractmethod
    def get_request_infos(self, start_time_in_millis, end_time_in_millis) -> Dict[str, List[RequestInfo]]:
        pass


class RedisMetricsStorage(MetricsStorage):
    def save_request_info(self, request_info: RequestInfo) -> None:
        pass

    def get_request_infos_by_api(self, api_name, start_time_in_millis, end_time_in_millis) -> List[RequestInfo]:
        pass

    def get_request_infos(self, start_time_in_millis, end_time_in_millis) -> Dict[str, List[RequestInfo]]:
        pass
import abc
import json
from typing import Dict

from PerformanceCounter import RequestInfo, RequestStat


class StatViewer(object):
    """
    接口类
    """
    @abc.abstractmethod
    def output(self, request_stats: Dict[str, RequestStat], start_time_in_millis, end_time_in_millis):
        pass
        "// format the requestStats to HTML style. // send it to email toAddresses."


class ConsoleViewer(StatViewer):
    def output(self, request_stats: Dict[str, RequestStat], start_time_in_millis, end_time_in_millis):
        print("Time Span: [" + start_time_in_millis + ", " + end_time_in_millis + "]")
        print(json.dumps(request_stats))


class EmailViewer(StatViewer):
    def output(self, request_stats: Dict[str, RequestStat], start_time_in_millis, end_time_in_millis):
        pass

    def __init__(self, email_sender=None, to_addresses=None):
        self.email_sender = email_sender or EmailSender()
        self.to_addresses = to_addresses or list()

    def add_to_address(self, address):
        self.to_addresses.append(address)


class EmailSender(object):
    pass

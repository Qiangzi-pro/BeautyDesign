"""
负责展示 OR 以一定频率统计&推送统计数据
"""
import abc
import json
import sched, time
from typing import Dict
from apscheduler.schedulers.blocking import BlockingScheduler
from PerformanceCounter import RequestStat
from PerformanceCounter.article40.MetricsStorage import MetricsStorage
from PerformanceCounter.article40.Aggregator import Aggregator


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


    def __init__(self, email_sender=None):
        self.email_sender = email_sender or EmailSender()
        self.to_addresses = list()

    def add_to_address(self, address):
        self.to_addresses.append(address)


class EmailSender(object):
    pass



class ConsoleReporter(object):
    def __init__(self, metrics_storage: MetricsStorage, aggregator: Aggregator, viewer: StatViewer):
        self.metrics_storage = metrics_storage
        self.aggregator = aggregator
        self.viewer = viewer
        self.executor = sched.scheduler(time.time, time.sleep)

    def start_repeated_report(self, period_in_seconds, duration_in_seconds):
        def action():
            duration_in_millis = duration_in_seconds * 1000
            end_time_in_millis = int(time.time() * 1000)
            start_time_in_millis = end_time_in_millis - duration_in_millis
            request_infos = self.metrics_storage.get_request_infos(start_time_in_millis, end_time_in_millis)
            request_stats: Dict[str, RequestStat] = self.aggregator.aggregate(request_infos, duration_in_millis)
            self.viewer.output(request_stats, start_time_in_millis, end_time_in_millis)
        self.executor.enter(period_in_seconds, 1, action=action)


class EmailReporter(object):
    """
    组装类，串联执行流程
    """
    DAY_HOURS_IN_SECONDS = 86400

    def __init__(self, metrics_storage: MetricsStorage, aggregator: Aggregator, viewer: StatViewer):
        self.metrics_storage = metrics_storage
        self.aggregator = aggregator
        self.viewer = viewer

    def start_daily_report(self):
        schedule = BlockingScheduler()

        def action():
            duration_in_millis = EmailReporter.DAY_HOURS_IN_SECONDS * 1000
            end_time_in_millis = int(time.time() * 1000)
            start_time_in_millis = end_time_in_millis - duration_in_millis
            request_infos = self.metrics_storage.get_request_infos(start_time_in_millis, end_time_in_millis)
            request_stats = self.aggregator.aggregate(request_infos, duration_in_millis)
            self.viewer.output(request_stats, start_time_in_millis, end_time_in_millis)

        schedule.add_job(action, "cron", day_of_week='0-7', hour=00, minute=00, second=00)
        schedule.start()



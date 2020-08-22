"""
负责展示 OR 以一定频率统计&推送统计数据
"""
import json
import sched, time
import sys
from typing import Dict, List
from collections import defaultdict
from apscheduler.schedulers.blocking import BlockingScheduler

from PerformanceCounter import RequestStat
from PerformanceCounter.article40.MetricsStorage import MetricsStorage, RedisMetricsStorage
from PerformanceCounter.article40.Aggregator import Aggregator
from .Viewer import StatViewer, ConsoleViewer, EmailViewer


class ScheduleReporter(object):
    MAX_STAT_DURATION_IN_MILLIS = 10 * 60 * 1000

    def __init__(self, metrics_storage: MetricsStorage, aggregator: Aggregator, viewer: StatViewer):
        self.metrics_storage = metrics_storage
        self.aggregator = aggregator
        self.viewer = viewer

    # def do_stat_and_report(self, start_time_in_millis, end_time_in_millis):
    #     duration_in_millis = end_time_in_millis - start_time_in_millis
    #     request_infos = self.metrics_storage.get_request_infos(start_time_in_millis, end_time_in_millis)
    #     request_stats: Dict[str, RequestStat] = self.aggregator.aggregate(request_infos, duration_in_millis)
    #     self.viewer.output(request_stats, start_time_in_millis, end_time_in_millis)

    def do_stat_and_report(self, start_time_in_millis, end_time_in_millis):
        stats = self.do_stat(start_time_in_millis, end_time_in_millis)
        self.viewer.output(stats, start_time_in_millis, end_time_in_millis)

    def do_stat(self, start_time_in_millis, end_time_in_millis):
        segment_stats: Dict[str, List[RequestStat]] = defaultdict(list)
        segment_start_time_millis = start_time_in_millis
        while segment_start_time_millis < end_time_in_millis:
            segment_end_time_millis = segment_start_time_millis + ScheduleReporter.MAX_STAT_DURATION_IN_MILLIS
            if segment_end_time_millis > end_time_in_millis:
                segment_end_time_millis = end_time_in_millis
            request_infos = self.metrics_storage.get_request_infos(segment_start_time_millis, segment_end_time_millis)
            if request_infos is None or not request_infos:
                continue

            segment_stat: Dict[str, RequestStat] = self.aggregator.aggregate(request_infos, segment_end_time_millis - segment_start_time_millis)
            self.add_stat(segment_stats, segment_stat)
            segment_start_time_millis += ScheduleReporter.MAX_STAT_DURATION_IN_MILLIS

        duration_in_millis = end_time_in_millis - start_time_in_millis
        aggregated_stats = self.aggregate_stats(segment_stats, duration_in_millis)
        return aggregated_stats

    def add_stat(self, segment_stats, segment_stat):
        for api_nam, stat in segment_stats.items():
            segment_stat[api_nam].append(stat)

    def aggregate_stats(self, segment_stats, duration_in_millis):
        aggregated_stats = dict()
        for api_name, api_stats in segment_stats.items():
            max_resp_time = sys.float_info.max
            min_resp_time = sys.float_info.min
            count = 0
            sum_resp_time = 0

            for stat in api_stats:
                if stat.max_response_time > max_resp_time:
                    max_resp_time = stat.max_response_time
                if stat.min_response_time < min_resp_time:
                    min_resp_time = stat.min_response_time
                count += stat.count
                sum_resp_time += (stat.count * stat.avg_response_time)

            aggregated_stat = RequestStat(
                max_response_time=max_resp_time,
                min_response_time=min_resp_time,
                avg_response_time=sum_resp_time / count,
                count=count,
                tps=count / duration_in_millis * 1000,
                p99_response_time=None,
                p999_response_time=None  # 待补充
            )
            aggregated_stats[api_name] = aggregated_stat

        return aggregated_stats


class ConsoleReporter(ScheduleReporter):
    def __init__(self, metrics_storage=None, aggregator=None, viewer=None):
        super().__init__(
            metrics_storage or RedisMetricsStorage(),
            aggregator or Aggregator(),
            viewer or ConsoleViewer
        )
        self.executor = sched.scheduler(time.time, time.sleep)

    def start_repeated_report(self, period_in_seconds, duration_in_seconds):
        def action():
            duration_in_millis = duration_in_seconds * 1000
            end_time_in_millis = int(time.time() * 1000)
            start_time_in_millis = end_time_in_millis - duration_in_millis
            self.do_stat_and_report(start_time_in_millis, end_time_in_millis)
        self.executor.enter(period_in_seconds, 1, action=action)


class EmailReporter(ScheduleReporter):
    """
    组装类，串联执行流程
    """
    DAY_HOURS_IN_SECONDS = 86400

    @classmethod
    def get_instance(cls, email_to_addresses):
        return cls(
            RedisMetricsStorage(),
            Aggregator(),
            EmailViewer(to_addresses=email_to_addresses)
        )

    def __init__(self, metrics_storage: MetricsStorage, aggregator: Aggregator, viewer: StatViewer):
        super().__init__(metrics_storage, aggregator, viewer)

    def start_daily_report(self):
        schedule = BlockingScheduler()

        def action():
            duration_in_millis = EmailReporter.DAY_HOURS_IN_SECONDS * 1000
            end_time_in_millis = int(time.time() * 1000)
            start_time_in_millis = end_time_in_millis - duration_in_millis
            self.do_stat_and_report(start_time_in_millis, end_time_in_millis)

        schedule.add_job(action, "cron", day_of_week='0-7', hour=00, minute=00, second=00)
        schedule.start()



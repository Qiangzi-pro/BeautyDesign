import time

from PerformanceCounter import RequestInfo
from PerformanceCounter.article40.MetricsCollector import MetricsCollector
from PerformanceCounter.article40.MetricsStorage import RedisMetricsStorage
from PerformanceCounter.article40.NewReporter40 import ConsoleReporter, EmailReporter


class PerfCounterTest(object):
    @staticmethod
    def main():
        console_reporter = ConsoleReporter()
        console_reporter.start_repeated_report(60, 60)

        email_to_addresses = []
        email_to_addresses.append("yuqiang.pro@gmail.com")
        email_reporter = EmailReporter.get_instance(email_to_addresses)
        email_reporter.start_daily_report()

        collector = MetricsCollector()
        collector.record_request(RequestInfo('register', 123, 10234))
        collector.record_request(RequestInfo('register', 223, 11234))
        collector.record_request(RequestInfo('register', 323, 12334))
        collector.record_request(RequestInfo('login', 123, 12434))
        collector.record_request(RequestInfo('login', 1223, 14234))

        try:
            time.sleep(10000)

        except InterruptedError as e:
            print(e)


if __name__ == '__main__':

    PerfCounterTest.main()
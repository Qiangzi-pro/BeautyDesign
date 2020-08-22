import time

from PerformanceCounter import RequestInfo
from PerformanceCounter.article26.MetricsCollector import MetricsCollector
from PerformanceCounter.article26.MetricsStorage import RedisMetricsStorage
from PerformanceCounter.article26.Reporter import ConsoleReporter


class PerfCounterTest(object):
    @staticmethod
    def main():
        # 使用方式暴露了太多细节给用户，过于灵活也带来了易用性的降低
        pass



if __name__ == '__main__':
    storage = RedisMetricsStorage()
    console_reporter = ConsoleReporter(storage)
    console_reporter.start_repeated_report(60, 60)

    collector = MetricsCollector(storage)
    collector.record_request(RequestInfo('register', 123, 10234))
    collector.record_request(RequestInfo('register', 223, 11234))
    collector.record_request(RequestInfo('register', 323, 12334))
    collector.record_request(RequestInfo('login', 123, 12434))
    collector.record_request(RequestInfo('login', 1223, 14234))

    try:
        time.sleep(10000)

    except InterruptedError as e:
        print(e)


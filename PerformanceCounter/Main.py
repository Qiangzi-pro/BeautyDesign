import time

from PerformanceCounter import RequestInfo
from PerformanceCounter.MetricsCollector import MetricsCollector
from PerformanceCounter.MetricsStorage import MetricsStorage, RedisMetricsStorage
from PerformanceCounter.Reporter import ConsoleReporter


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

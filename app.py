from prometheus_client import start_http_server, Gauge, Summary, Counter, Histogram, Info, Enum
import prometheus_client as prom
import random
import time

# Remove default metrics
prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
prom.REGISTRY.unregister(prom.GC_COLLECTOR)

counter     = Counter('counder_demo', 'Description of counter', ['method', 'endpoint'])
gauge       = Gauge("gauge_demo", "Description of gauge")
summary     = Summary('summary_demo', 'Description of summary')
histogram   = Histogram('histogram_demo', 'Description of histogram')
info        = Info('info_demo', 'Description of info')
enumerate   = Enum('enum_demo', 'Description of enum', states=['starting', 'running', 'stopped'])

def counter_metric(t):
    counter.inc()    # Increment by 1
    counter.inc(t)   # Increment by given value
    # counter.labels(method='get', endpoint='/').inc()
    # counter.labels(method='post', endpoint='/submit').inc(1.0, {'trace_id': 'def456'})

def gauge_metric(t):
    gauge.inc()      # Increment by 1
    gauge.dec(t)     # Decrement by given value
    gauge.set(t)     # Set to a given value

def summary_metric():
    summary.observe(4.7)     # Observe 4.7 (seconds in this case)
    
def histogram_metric():
    histogram.observe(4.7)   # Observe 4.7 (seconds in this case)

def info_metric(t):
    info.info({'version': '1.2.3', 'buildhost': 'foo@bar', 'random': str(t)})

def enum_metric():
    enumerate.state('running')
    enumerate.state('stopped')
    enumerate.state('stopped')


if __name__ == '__main__':
    start_http_server(9000)
    while True:
        rand = random.random()

        counter_metric(rand)
        gauge_metric(rand)
        summary_metric()
        histogram_metric()
        info_metric(rand)
        enum_metric()
## Prometheus Metrics
Prometheus uses a pull model to collect these metrics; that is, Prometheus scrapes HTTP endpoints that expose metrics. 

### Metric types
Prometheus provides 4 different types of metrics which work in most situations, all wrapped up in a convenient client library. 

### 1. Counters
The counter metric type is used for any value that increases, such as a request count or error count.

#### When to use counters?
- you want to record a value that only goes up
- you want to be able to later query how fast the value is increasing (i.e. it’s rate)

#### What are some use cases for counters?
- request count
- tasks completed
- error count

#### Java client for counters
```java
package com.dakual.controller;
import io.prometheus.client.CollectorRegistry;
import io.prometheus.client.Counter;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CounterController {
    private final Counter requestCount;
    public CounterController(CollectorRegistry collectorRegistry) {
        requestCount = Counter.build()
                .name("request_count")
                .help("Number of hello requests.")
                .register(collectorRegistry);
    }
    @GetMapping(value = "/hello")
    public String hello() {
        requestCount.inc();
        return "Hi!";
    }
}
```

#### Python Client for counters
```py
from prometheus_client import Counter
c = Counter('my_failures', 'Description of counter')
c.inc()     # Increment by 1
c.inc(1.6)  # Increment by given value
```

#### How can I query counters in Prometheus? The PromQL query.
We can use the following query to calculate the per second rate of requests averaged over the last 5 minutes:
```
rate(request_count[5m])
```

### 2. Gauges
The gauge metric type can be used for values that go down as well as up, such as current memory usage or the number of items in a queue.

#### When to use gauges?
- you want to record a value that can go up or down
- you don’t need to query its rate

#### What are some use cases for gauges?
- memory usage
- queue size
- number of requests in progress

#### Java client for gauges
```java
package com.dakual.controller;
import io.prometheus.client.CollectorRegistry;
import io.prometheus.client.Gauge;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GaugeController {
    private final Gauge queueSize;
    public GaugeController(CollectorRegistry collectorRegistry) {
        queueSize = Gauge.build()
                .name("queue_size")
                .help("Size of queue.")
                .register(collectorRegistry);
    }
    @GetMapping(value = "/push")
    public String push() {
        queueSize.inc();
        return "You pushed an item to the queue!";
    }
    @GetMapping(value = "/pop")
    public String pop() {
        queueSize.dec();
        return "You popped an item from the queue!";
    }
}
```

#### Python Client for gauges
```py
from prometheus_client import Gauge
g = Gauge('my_inprogress_requests', 'Description of gauge')
g.inc()      # Increment by 1
g.dec(10)    # Decrement by given value
g.set(4.2)   # Set to a given value
```

#### How can I query gauges in Prometheus? The PromQL query.
```
avg_over_time(queue_size[5m])
```

### 3. Histograms
The histogram metric type measures the frequency of value observations that fall into specific predefined buckets.

#### When to use histograms?
- you want to take many measurements of a value, to later calculate averages or percentiles
- you’re not bothered about the exact values, but are happy with an approximation
- you know what the range of values will be up front, so can use the default bucket definitions or define your own

#### What are some use cases for histograms?
- request duration
- response size

#### Java client for histograms
```java
package com.dakual.controller;
import io.prometheus.client.CollectorRegistry;
import io.prometheus.client.Histogram;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import static java.lang.Thread.sleep;

@RestController
public class HistogramController {
    private final Histogram requestDuration;
    public HistogramController(CollectorRegistry collectorRegistry) {
        requestDuration = Histogram.build()
                .name("request_duration")
                .help("Time for HTTP request.")
                .register(collectorRegistry);
    }
    @GetMapping(value = "/wait")
    public String makeMeWait() throws InterruptedException {
        Histogram.Timer timer = requestDuration.startTimer();
        long sleepDuration = Double.valueOf(Math.floor(Math.random() * 10 * 1000)).longValue();
        sleep(sleepDuration);
        timer.observeDuration();
        return String.format("I kept you waiting for %s ms!", sleepDuration);
    }
}
```

#### Python Client for histograms
```py
from prometheus_client import Histogram
h = Histogram('request_latency_seconds', 'Description of histogram')
h.observe(4.7)    # Observe 4.7 (seconds in this case)
```

#### How can I query histograms in Prometheus? The PromQL query.
```
rate(request_duration_sum[5m])
/
rate(request_duration_count[5m])
```
```
histogram_quantile(0.95, sum(rate(request_duration_bucket[5m])) by (le))
```

### 4. Summaries
Summaries and histograms share a lot of similarities. Summaries preceded histograms, and the recommendation is very much to use histograms where possible. 

#### When to use summaries?
- you want to take many measurements of a value, to later calculate averages or percentiles
- you’re not bothered about the exact values, but are happy with an approximation
- you don’t know what the range of values will be up front, so cannot use histograms
#### What are some use cases for summaries?
- request duration
- response size

#### Java client for summaries

```java
package com.java.controller;
import io.prometheus.client.CollectorRegistry;
import io.prometheus.client.Summary;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import static java.lang.Thread.sleep;

@RestController
public class SummaryController {
    private final Summary requestDuration;
    public SummaryController(CollectorRegistry collectorRegistry) {
        requestDuration = Summary.build()
                .name("request_duration_summary")
                .help("Time for HTTP request.")
                .quantile(0.95, 0.01)
                .register(collectorRegistry);
    }
    @GetMapping(value = "/waitSummary")
    public String makeMeWait() throws InterruptedException {
        Summary.Timer timer = requestDuration.startTimer();
        long sleepDuration = Double.valueOf(Math.floor(Math.random() * 10 * 1000)).longValue();
        sleep(sleepDuration);
        timer.observeDuration();
        return String.format("I kept you waiting for %s ms!", sleepDuration);
    }
}
```

#### Python Client for summaries
```py
from prometheus_client import Summary
s = Summary('request_latency_seconds', 'Description of summary')
s.observe(4.7)    # Observe 4.7 (seconds in this case)
```

#### How can I query summaries in Prometheus? The PromQL query.
```
rate(request_duration_summary_sum[5m])
/
rate(request_duration_summary_count[5m])
```
```
request_duration_summary{quantile="0.95"}
```

### 5. Info
Info tracks key-value information, usually about a whole target.

#### Python Client for Info
```py
from prometheus_client import Info
i = Info('my_build_version', 'Description of info')
i.info({'version': '1.2.3', 'buildhost': 'foo@bar'})
```

### 6. Enum
Enum tracks which of a set of states something is currently in.

#### Python Client for Enums
```py
from prometheus_client import Enum
e = Enum('my_task_state', 'Description of enum',
        states=['starting', 'running', 'stopped'])
e.state('running')
```


#### Labels
All metrics can have labels, allowing grouping of related time series.
```py
from prometheus_client import Counter
c = Counter('my_requests_total', 'HTTP Failures', ['method', 'endpoint'])
c.labels(method='get', endpoint='/').inc()
c.labels(method='post', endpoint='/submit').inc()
```

#### Exemplars
Exemplars can be added to counter and histogram metrics. Exemplars can be specified by passing a dict of label value pairs to be exposed as the exemplar. 

```py
from prometheus_client import Counter
c = Counter('my_requests_total', 'HTTP Failures', ['method', 'endpoint'])
c.labels('get', '/').inc(exemplar={'trace_id': 'abc123'})
c.labels('post', '/submit').inc(1.0, {'trace_id': 'def456'})
```
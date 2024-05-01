#!/usr/bin/env python3
"""
Network Monitoring with Prometheus

Module sets up an HTTP server to expose prometheus metrics for monitoring
network traffic on a system. It collects statistics for each network
interface using the 'psutil' and 'ping3' libraries and updates Prometheus
metrics with the average rtt, count of packets sent and received

Metrics:
- `avg_rtt`: avg_rtt to dest
- `packets_sent`: Number of packets sent by each network interface.
- `packets_received`: Number of packets received by each network interface.
"""

import random
import logging
import statistics
from itertools import islice
from flask import Flask, Response
from prometheus_client import Counter, Gauge, generate_latest
from ping3 import ping
import psutil


# Create a Prometheus Gauge to represent a custom metric
custom_gauge = Gauge(
    "custom_metric",
    "A custom metric based on a parameter",
)

logger = logging.getLogger(__name__)
app = Flask(__name__)
CONTENT_TYPE_LATEST = str("text/plain; version=0.0.4; charset=utf-8")

number_of_requests = Counter(
    "number_of_requests",
    "The number of requests, its a counter so the value can increase or reset to zero.",
)

current_memory_usage = Gauge(
    "current_memory_usage_locally",
    "The current value of memory usage, its a gauge so it can go up or down.",
    ["server_name"],
)

# Set up a gauge to track the ping results
ping_gauge = Gauge(
    "avg_rtt",
    "Ping time to specific hosts",
    ["dest"],
)

# List of hosts to ping
hosts_to_ping = [
    "192.168.1.1",
    "www.google.com",
    "www.netflix.com",
    "www.cnn.com",
]

# Create a Gauge metric to hold the packets sent by each network interface
packet_sent_gauge = Gauge(
    "packets_sent",
    "Packets sent by each network interface",
    ["ifname"],
)

# Create a Gauge metric to hold the packets sent by each network interface
packet_received_gauge = Gauge(
    "packets_recv",
    "Packets received by each network interface",
    ["ifname"],
)


def update_ping_gauge():
    """Define a function to update the gauge with ping results"""
    number_of_pings = 5
    for host in hosts_to_ping:
        # creates an iterator of pings to host that stops at `None`
        def ping_host(host: str):
            return iter(lambda: ping(host, unit="ms", timeout=2), None)

        # takes at most `number_of_pings` rtt from ping_host
        take_n_pings = list(islice(ping_host(host), number_of_pings))
        # takes the mean of the list of valid ping times 0 for invalid pings
        ping_gauge.labels(dest=host).set(
            statistics.mean(take_n_pings if take_n_pings else [0])
        )


def update_packets_by_interface():
    """
    Define a function that collects the packets sent and received by each
    network interface
    """
    net_io_counters = psutil.net_io_counters(pernic=True)
    # Update the metric with the latest packets sent count for each interface
    for interface, counters in net_io_counters.items():
        packet_sent_gauge.labels(ifname=interface).set(
            counters.packets_sent,
        )
        packet_received_gauge.labels(ifname=interface).set(
            counters.packets_recv,
        )


@app.route("/metrics", methods=["GET"])
def get_data():
    """Returns all data as plaintext."""
    number_of_requests.inc()
    current_memory_usage.labels("server-a").set(random.randint(10000, 90000))
    update_ping_gauge()
    update_packets_by_interface()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

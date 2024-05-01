
# Table of Contents

1.  [Assumptions](#orgfad3c96)
    1.  [Python](#orgb3e2956)
        1.  [Installing without NixOS](#org4ead8f1)
        2.  [Installing without NixOS](#org5e794d0)
    2.  [Prometheus](#org5d04d13)
2.  [Design](#org7a08c99)
    1.  [Average Ping RTT(`avg_rtt`)](#org6cf0cb4)
        1.  [Ping3](#org3b9ceca)
        2.  [`app.py`](#org0bf5ed6)
        3.  [Results](#orgc7cfeba)
    2.  [Number of Packets Sent(`packets_sent`)](#org5389892)
        1.  [psutils](#org6c1c0a7)
        2.  [`app.py`](#orgaee2bdd)
        3.  [Results](#org3df5d0e)
    3.  [Number of Packets Received(`packets_recv`)](#org1270ede)
        1.  [psutil](#org77d656c)
        2.  [`app.py`](#orgb0a3b91)
        3.  [Results](#orge3a829b)
3.  [`app.py`](#orgad7d86e)
4.  [`shell.nix`](#org6d974dd)



<a id="orgfad3c96"></a>

# Assumptions

The source code for this project can be found here if any build issues occur from the files submitted on canvas:

    git clone https://github.com/cesarrochasjsu/cs158b-project.git
    cd cs158b-project


<a id="orgb3e2956"></a>

## Python

This Python<sup><a id="fnr.1" class="footref" href="#fn.1" role="doc-backlink">1</a></sup> project was developed using NixOS<sup><a id="fnr.2" class="footref" href="#fn.2" role="doc-backlink">2</a></sup> and tested on Ubuntu <sup><a id="fnr.3" class="footref" href="#fn.3" role="doc-backlink">3</a></sup>. However, a non-NixOS user can use Python&rsquo;s pip <sup><a id="fnr.4" class="footref" href="#fn.4" role="doc-backlink">4</a></sup> and `requirements.py` (Figure [2](#orga546112)) to run it.


<a id="org4ead8f1"></a>

### Installing without NixOS

It&rsquo;s really easy to install this project through a `requirements.py` file.

    black==24.4.0
    blinker==1.7.0
    click==8.1.7
    Flask==3.0.3
    itsdangerous==2.2.0
    Jinja2==3.1.3
    MarkupSafe==2.1.5
    mypy-extensions==1.0.0
    packaging==24.0
    pathspec==0.12.1
    ping3==4.0.8
    platformdirs==4.2.1
    prometheus_client==0.20.0
    psutil==5.9.8
    tomli==2.0.1
    typing_extensions==4.11.0
    Werkzeug==3.0.2

You can try using virtual env so that it doesn&rsquo;t pollute your global python

    python3 -m venv .venv

Then hop in using:

    source .venv/bin/activate

Then typing:

    pip install -r requirements.py

then running the app by:

    python3 app.py


<a id="org5e794d0"></a>

### Installing without NixOS

If you&rsquo;ve downloaded this project and have the Nix<sup><a id="fnr.5" class="footref" href="#fn.5" role="doc-backlink">5</a></sup> package manager, then type

    nix-build

and then use this to run the app

    ./result/bin/app.py


<a id="org5d04d13"></a>

## Prometheus

The next assumption is that you have a way to run prometheus <sup><a id="fnr.6" class="footref" href="#fn.6" role="doc-backlink">6</a></sup>. The `prometheus.yml` file has been provided (Figure [9](#org52eeb3f)) and so are the instructions to run it (Figure [10](#orgbaccbdf)).

I assume you have a prometheus scraper that is scraping localhost:5000.

    global:
      scrape_interval:     10s # By default, scrape targets every 15 seconds.
    
    
    # A scrape configuration containing exactly one endpoint to scrape:
    # Here it's Prometheus itself.
    scrape_configs:
      # The job name is added as a label `job=<job_name>` to any
      # timeseries scraped from this config.
      - job_name: 'cs-158b-project'
    
        # Override the global default and scrape targets from this job
        # every 5 seconds.
        # scrape_interval: 5s
        static_configs:
          - targets: [ 'localhost:5000']

    prometheus --config.file=prometheus.yml


<a id="org7a08c99"></a>

# Design


<a id="org6cf0cb4"></a>

## Average Ping RTT(`avg_rtt`)


<a id="org3b9ceca"></a>

### Ping3

Average Ping RTT was calculated using ping3 <sup><a id="fnr.7" class="footref" href="#fn.7" role="doc-backlink">7</a></sup> library&rsquo;s `ping` function in python

    from ping3 import ping
    
    return f"Ping something that exists: {ping('google.com', unit='ms')}"

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
<caption class="t-above"><span class="table-number">Table 1:</span> result from pinging &ldquo;www.google.com&rdquo;</caption>

<colgroup>
<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left">Ping something that exists: 59.302568435668945</td>
</tr>
</tbody>
</table>

    from ping3 import ping
    
    return f"Ping something that does not exist: {ping('www.netflix.com')}"

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
<caption class="t-above"><span class="table-number">Table 2:</span> Python output from something that does not exist</caption>

<colgroup>
<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left">Ping something that does not exist: None</td>
</tr>
</tbody>
</table>

To collect these pings, we want to collect create an iterable to pass to `statistics.mean`. A `ping_host` function that contains an iterator that returns the next valid ping was used to generate the dataset in combination with `islice` to take at most 5 pings.

    from ping3 import ping
    from itertools import islice
    number_of_pings = 5
    
    def ping_host(host: str):
        return iter(lambda: ping(host, unit="ms", timeout=2), None)
    
    return list(islice(ping_host("google.com"), number_of_pings))

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />

<col  class="org-right" />
</colgroup>
<tbody>
<tr>
<td class="org-right">58.83932113647461</td>
<td class="org-right">58.669090270996094</td>
<td class="org-right">57.837486267089844</td>
<td class="org-right">57.84034729003906</td>
<td class="org-right">57.858943939208984</td>
</tr>
</tbody>
</table>

Timeout is useful for when the ping takes too long, or host doesn&rsquo;t exist. The `None` argument in the `iter` tells it to leave when the ping is invalid, only generating a valid dataset that can be passed to `statistics.mean`.

    from ping3 import ping
    from itertools import islice
    number_of_pings = 5
    
    def ping_host(host: str):
        return iter(lambda: ping(host, unit="ms", timeout=2), None)
    
    return list(islice(ping_host("netflix.com"), number_of_pings))


<a id="org0bf5ed6"></a>

### `app.py`

To record the ping results in `app.py`, A `Gauge` that keeps track of pings, and a list of hosts to ping was created.

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

See Figure [16](#org3a4b814) for the implementation of the updated gauge in `app.py`. Figure [17](#orge29ced1) shows how the `update_ping_gauge` function is used in `app.py` to collect information about `avg_rtt` for scraping.

    @app.route("/metrics", methods=["GET"])
    def get_data():
        """Returns all data as plaintext."""
        number_of_requests.inc()
        current_memory_usage.labels("server-a").set(random.randint(10000, 90000))
        update_ping_gauge()
        update_packets_by_interface()
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


<a id="orgc7cfeba"></a>

### Results

![img](/home/nixer/2024-04-28-172352_1597x764_scrot.png "prometheus scraping localhost:9090 for `avg_rtt`. Unreachable destinations are marked as $0$")

![img](/home/nixer/2024-04-28-172245_1592x829_scrot.png "prometheus scraping localhost:9090 for `avg_rtt` of &ldquo;www.google.com&rdquo;")


<a id="org5389892"></a>

## Number of Packets Sent(`packets_sent`)


<a id="org6c1c0a7"></a>

### psutils

The psutil<sup><a id="fnr.8" class="footref" href="#fn.8" role="doc-backlink">8</a></sup> library can be used to monitor the number of packets sent by interface. The net\_io\_counters <sup><a id="fnr.9" class="footref" href="#fn.9" role="doc-backlink">9</a></sup> method returns network I/O statistics as a named tuple. Using the `pernic=True` variable will return that named tuple for all network interface names.

    import psutil
    
    return psutil.net_io_counters(pernic=True)['lo'].packets_sent

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
<caption class="t-above"><span class="table-number">Table 3:</span> results of looking up interface <code>lo</code> using <code>psutil</code> to find packets sent</caption>

<colgroup>
<col  class="org-right" />
</colgroup>
<tbody>
<tr>
<td class="org-right">21407</td>
</tr>
</tbody>
</table>


<a id="orgaee2bdd"></a>

### `app.py`

A packets sent gauge was created to keep track of packets sent per network interface

    # Create a Gauge metric to hold the packets sent by each network interface
    packet_sent_gauge = Gauge(
        "packets_sent",
        "Packets sent by each network interface",
        ["ifname"],
    )

To fill in the packet sent gauge, a function named `update_packets_by_interface` function was created to loop through all network interfaces in `psutil.net_io_counters(pernic=True)` and collect the packets sent.

    def update_packets_by_interface():
        net_io_counters = psutil.net_io_counters(pernic=True)
    
        # Update the metric with the latest packets sent count for each interface
        for interface, counters in net_io_counters.items():
            packet_sent_gauge.labels(ifname=interface).set(
                counters.packets_sent,
            )

The `update_packets_sent_by_interface` function was used in `app.py` in the `get_data` function (Figure [17](#orge29ced1)).


<a id="org3df5d0e"></a>

### Results

![img](/home/nixer/2024-04-28-184957_1599x841_scrot.png "prometheus query for `packets_sent` in localhost:9090 scraping localhost:5000")

![img](/home/nixer/2024-04-28-185252_1596x542_scrot.png "prometheus query for `packets_sent` for `ifname=lo` in localhost:9090 scraping localhost:5000")


<a id="org1270ede"></a>

## Number of Packets Received(`packets_recv`)


<a id="org77d656c"></a>

### psutil

To obtain the number of packets received per network interface,

    import psutil
    
    return psutil.net_io_counters(pernic=True)['lo'].packets_recv

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
<caption class="t-above"><span class="table-number">Table 4:</span> results of looking up interface <code>lo</code> using <code>psutil</code> to find packets received</caption>

<colgroup>
<col  class="org-right" />
</colgroup>
<tbody>
<tr>
<td class="org-right">21407</td>
</tr>
</tbody>
</table>


<a id="orgb0a3b91"></a>

### `app.py`

To collect the packets received per network interface, a packets received gauge was created

    
    # Create a Gauge metric to hold the packets sent by each network interface
    packet_received_gauge = Gauge(
        "packets_recv",
        "Packets received by each network interface",
        ["ifname"],
    )

    def update_packets_by_interface():
        net_io_counters = psutil.net_io_counters(pernic=True)
    
        # Update the metric with the latest packets sent count for each interface
        for interface, counters in net_io_counters.items():
            packet_sent_gauge.labels(ifname=interface).set(
                counters.packets_sent,
            )
            packet_received_gauge.labels(ifname=interface).set(
                counters.packets_recv,
            )


<a id="orge3a829b"></a>

### Results

![img](/home/nixer/2024-04-28-190104_1599x832_scrot.png "prometheus query for `packets_recv` in localhost:9090 scraping localhost:5000")

![img](/home/nixer/2024-04-28-190257_1600x521_scrot.png "prometheus query for `packets_recv` in localhost:9090 scraping localhost:5000")


<a id="orgad7d86e"></a>

# `app.py`

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
            ping_times = []
            for _ in range(number_of_pings):
                rtt = ping(host, unit="ms")
                if not rtt:
                    # spending too long on timeout or non existing pings
                    # wastes time and energy.
                    ping_times.append(0)
                    break
                ping_times.append(rtt)
            # Take a mean of the list of five pings
            ping_gauge.labels(dest=host).set(statistics.mean(ping_times))
    
    
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


<a id="org6d974dd"></a>

# `shell.nix`

    { pkgs ? import <nixpkgs> { } }:
    
    let
      # Overriding the default 'ping3' package with custom source details
      customPing3 = pkgs.python3Packages.buildPythonPackage rec {
        pname = "ping3";
        version = "4.0.8";
        format = "wheel";
    
        src = pkgs.fetchurl {
          url = "https://files.pythonhosted.org/packages/e6/f4/4070daca3da5bbc"
            + "3ef5e622d68f979e034e5bf678416817918e51a1b2907/"
            + "ping3-4.0.8-py3-none-any.whl";
          sha256 = "152mj8qrqhbphrm46jsr451bh714g0kjb7gnkag25d38362r9hmm";
        };
        # Disable tests, as they might not be needed for this context
        doCheck = false;
      };
    
      # Create a Python environment with additional packages,
      # including the custom 'ping3'
      myPythonEnv = pkgs.python3.withPackages (ps: with ps; [ customPing3 ]);
    
    in pkgs.mkShell {
      # The build inputs for the Nix shell include the
      # Python environment with customizations
      buildInputs = [
        # installing ping3
        myPythonEnv
        # installing prometheus
        pkgs.prometheus
        # installing pyton packages from nixpkgs
        (with pkgs.python3Packages; [
          pylint
          black
          flask
          psutil
          jinja2
          prometheus-client
        ])
        # installing LaTeX for report writing
        (pkgs.texlive.combine {
          inherit (pkgs.texlive)
            scheme-full beamer latexmk wrapfig ulem capt-of
            collection-fontsrecommended amsmath hyperref;
        })
      ];
    }


# Footnotes

<sup><a id="fn.1" href="#fnr.1">1</a></sup> Python. <https://www.python.org/>

<sup><a id="fn.2" href="#fnr.2">2</a></sup> NixOS. <https://nixos.org/>

<sup><a id="fn.3" href="#fnr.3">3</a></sup> Ubuntu. <https://cdimage.ubuntu.com/ubuntu-server/jammy/daily-live/20231208/>

<sup><a id="fn.4" href="#fnr.4">4</a></sup> Pip. <https://pip.pypa.io/en/stable/installation/>

<sup><a id="fn.5" href="#fnr.5">5</a></sup> Nix Package manager. <https://nixos.org/download/>

<sup><a id="fn.6" href="#fnr.6">6</a></sup> Prometheus. <https://prometheus.io/>

<sup><a id="fn.7" href="#fnr.7">7</a></sup> Ping3. <https://pypi.org/project/ping3/>

<sup><a id="fn.8" href="#fnr.8">8</a></sup> psutil. <https://pypi.org/project/psutil/>

<sup><a id="fn.9" href="#fnr.9">9</a></sup> net\_iocounters. <https://psutil.readthedocs.io/en/latest/#psutil.net_io_counters>

"""Application exporter"""
# ref https://trstringer.com/quick-and-easy-prometheus-exporter/
# Author: Andres Kepler <andres.kepler@entigo.com>
# Date: 11.02.2022
# This app demonstrates prometheus exporter by fetching Estonian Wheather Stations data.
import json
import logging
import os
import time
from socketserver import ThreadingMixIn
import threading
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer
from prometheus_client import Summary, Gauge, Enum, make_wsgi_app
from prometheus_client.core import REGISTRY
from ws import emhi_xml
from util import health


metrics = {
            "airtemperature": ["Gauge","Current air temperature"],
            "airpressure": ["Gauge","Current air pressure"],
            "precipitations": ["Gauge","Current precipitations"],
            "relativehumidity": ["Gauge","Current relative humidity"],
            "uvindex": ["Gauge","Current UV Index"],
            "visibility": ["Gauge","Current visibility"],
            "winddirection": ["Gauge","Wind direction"],
            "windspeed": ["Gauge","Current wind speed"],
            "windspeedmax": ["Gauge","Wind gust"],
            }

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """Thread per request HTTP server."""
    # Make worker threads "fire and forget". Beginning with Python 3.7 this
    # prevents a memory leak because ``ThreadingMixIn`` starts to gather all
    # non-daemon threads in a list in order to join on them at server close.
    daemon_threads = True

class _SilentHandler(WSGIRequestHandler):
    """WSGI handler that does not log requests."""

    def log_message(self, format, *args):
        """Log nothing."""


def start_wsgi_server(port, addr='', registry=REGISTRY):
    """Starts a WSGI server for prometheus metrics as a daemon thread."""
    app = Flask(__name__)

    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app, {"/metrics": make_wsgi_app(registry),
                       "/healthz": health}
    )

    httpd = make_server(addr, port, app, ThreadingWSGIServer, handler_class=_SilentHandler)
    t = threading.Thread(target=httpd.serve_forever)
    t.daemon = True
    t.start()


class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=60):
        self.polling_interval_seconds = polling_interval_seconds
        self.gauge = Gauge('ws_metrics', 'Weather station metrics', ['name', 'location','desc'])

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    @REQUEST_TIME.time()
    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        # Fetch raw status data from the application
        # weather_station = os.getenv("EMHI_STATION", "Tallinn-Harku")
        ws_data = emhi_xml()
        for ws in ws_data:
            weather_station = ws['name']
            for key, value in metrics.items():
                if weather_station == value:
                    continue
                metric_value=ws.get(key,0)
                if not metric_value:
                    continue
                self.gauge.labels(key, weather_station, value[1]).set(metric_value)
                logging.debug(f"{weather_station}, {key}={metric_value}=>{value[1]}")

def main():
    """Main entry point"""
    logging.basicConfig(level=logging.DEBUG if os.getenv("DEBUG", "false") == "true" else logging.INFO)
    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "60"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    logging.info(f"Starting WS Poller at port {exporter_port}")
    start_wsgi_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
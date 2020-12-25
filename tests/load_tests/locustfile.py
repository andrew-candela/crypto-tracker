# Third party modules
from locust import HttpUser, between, task


class WebUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def list_metrics(self):
        self.client.get("/list-metrics")

    @task
    def list_metric_performance(self):
        self.client.get(
            "/metrics",
            params={'metric': 'price', 'dimension': 'market:bitstamp:omggbp'}
        )

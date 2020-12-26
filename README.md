# Crypto Metrics Tracker

Welcome to the Crypto-Metrics tracker!
This is a toy app designed to track Crypto metrics and send alerts based on simple thresholds.

The app itself consists of two lambda functions running behind an API gateway.
There is a third lambda function running on a 1 minute timer to collect data.
I use a Postgres RDS for the storage layer.
The `terraform/` folder has all of the configuration needed to run the app in your own account.

## Usage

Every 5 minutes the app collects the latest metrics from
[CryptoWatch's API](https://docs.cryptowat.ch/rest-api/).
Right now the only metric I collect is `price`.
The app stores those metrics in a database,
and then compares the latest metrics with the averages over the last 24 hours.

You can have the app notify you when a metric value exceeds 3x the 24 hr rolling average.

You can also query the app for historical metrics.

### A note about LiveCoin and CryptoWatch

This project originally used LiveCoin to gather crypto metrics.
Some bad actors made it into Livecoin's systems and
[caused some problems](https://www.zdnet.com/article/russian-crypto-exchange-livecoin-hacked-after-it-lost-control-of-its-servers/#ftag=RSSbaffb68).
They drove up the bitcoin price to about 10x higher than it should have been,
and then presumably liquidated their assets with the inflated price.
All this is very interesting, but it has resulted in removal of the public API.
I'll need to find something else to collect metrics from.

Looks like I can get some data from CryptoWatch's public API.
Their limits can support polling every 5 mins.
That's fine for the purposes of this project.

### Email: /emails

Sign up for email alerts with a post request:

```Shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"email":"your_email@email.com"}' \
  "${API_BASE}/emails"
```

Remove your email with a DELETE:

```Shell
curl --header "Content-Type: application/json" \
  --request DELETE \
  --data '{"email":"your_email@email.com"}' \
  "${API_BASE}/emails"
```

See what emails are in the list with a GET:

```Shell
curl "${API_BASE}/emails"
```

### Metrics: /metrics and /list-metrics

Find the metrics and Dimensions available with a GET to `/list-metrics`:

```Shell
curl "${API_BASE}/list-metrics"
```

Get a graph of metric performance and rank of standard dev of
the metric against the same metric of other dimensions with a GET to `/metrics`:

```Shell
curl "${API_BASE}/metrics?metric=${your_metric}&dimension=${your_dimension}"
```

## Local Dev

To set up a local environment do the following:

- copy .env.example to .env `cp .env.example .env`
- fill out the .env file with your app's parameters. `PG_HOST` should be `localhost` in this case.
- run `docker-compose up -d` to start a postgres DB in the background
- activate your virtual env and install requirements
- install the package itself: `pip install -e .`
- run the migration script to create the tables in the DB: `python scripts/run_migrations.py`
- hack away

I've included `if __name__ == '__main__' ...` blocks in each of the
files for the lambda functions for convenience.

## Deploying to production

The app is made up of 2 lambda functions behind an API gateway,
and 1 lambda function running on a timer.

When deploying your code to master (actually any branch), a Github Actions workflow
will package up your code and deploy it to S3 where it is used
to update the three lambda functions.
You'll have to add some secrets to your github repo in order for this step to work
with your own AWS account.

## Creating infra with Terraform

Use the terraform files to generate the following ifra:

- a postgres database and VPC etc
- the lambda functions and permissions
- API gateway stuff

You will need to first [install terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)
on your system.
Then, navigate to the `terraform` folder and run `terraform init`.
Once Terraform has initialized your project, you can fire up the
needed infra with `terraform apply`.
Terraform will show you all of the things that it is about to create
and if you're happy with it type `yes`.

If you haven't yet uploaded a code package to S3, Terraform will
fail to create the lambda functions.
You can re-run `terraform apply` once you've deployed this project
to s3.

Once you've created your Database in AWS,
you will need to run the migration script to create the needed
tables:

```Shell
# back up to previous dir if you haven't already
cd ../
python scripts/run_migrations.py
```

## Run tests

I use pytest to run the test suite.
run the tests like this:

```Shell
# run unit tests
pytest tests/unit
# run integration tests
pytest test/integration
```

Make sure you have activated your virtual env.
If you haven't already installed the package itself into your virtual env
then you will have to run: `pip install -e .`.
If pytest can't find the `service` package then this is probably the reason.

## Productionizing

There are a few shortcuts that I've taken here.
I think the app is fairly scalable the way it is,
but I could make some improvements in the following areas.

### Scaling Postgres

Using Postgres for the persistence layer works fairly well with
small to medium sized amounts of data.
The index on time/dimension fields in the metrics table speeds up
operations a bit, but Postgres will eventually struggle as I get:

- more metrics per row (a columnar DB would be nice for this)
- more records per unit of time
- more frequent requests per unit of time

If api.livecoin.net ever comes back online,
I can probably fit a full day's worth of metrics (about 1.4MM records)
in my `db.t2.micro` RDS, and support a handful of requests for metrics per second.
We'll see..

### Handling metric 'anomoly' checks better

Currently I'm doing a nested loop over all metrics of all dimensions (about 1000)
and all metrics (about 10) to get a list of all the metrics that should trigger an alarm.
This happens once a minute, and is fairly fast now.
If I tracked more than 10 metrics - say 1000 - then this app would fall over.
Postgres would have a hard time storing and fetching that many columns as we mentioned above,
and my anomoly loop would take much longer, in addition to requiring a lot of memory.

### Querying the metrics through the API often

If we assume that the size of the data in Postgres remains fixed,
then this app should do fairly well to serve multiple requests per second.

The main issues I can see are:

#### My app doesn't share DB connections

I don't know how to do connection pooling with API gateway...
Oh, there is a
[product](https://aws.amazon.com/blogs/compute/using-amazon-rds-proxy-with-aws-lambda/)
for that. OK so this could have been addressed.

#### The app doesn't cache any results

If this was a popular app then I would like to not have to
re-compute the standard deviation of every metric every time someone
makes a request.

I could create a materialized view with the Standard Dev's for each
metric and updated it every minute when I gather new metrics.
Then all the app would have to do to serve a request for metrics is
select from that static table to compute the metric ranks.

#### Load test results

I tried load testing with [locust.io](https://locust.io/).
The app managed to hold up to about 5 RPS against the `/metrics` and `/list-metrics`
endpoints simultaneously, with DB CPU reaching about 50%.
I tried cranking it up to 20 RPS, but that's when the app started having trouble.
Postgres CPU spiked to about 80%, and the lambda function invocations started timing out.

I think the most effective way to support more requests per second would be to
re-materialize a view with all requestable metrics each time I bring in new data.
Since this data only changes once every 5 minutes, the extra computation is nothing
compared to the savings I'd get by not doing it for every request.

If I do that, I suspect I could serve 20 requests or more per second without increasing
any resources.

### Collecting metrics more frequently

I feel like something like Flink would be a better solution
than Postgres if we wanted to update metrics say, every second.
I don't have a ton of experience with stream aggregation though, so I'd
reach for it when I know have a bit more time to experiment.

### Monitoring Metrics and watching for failures

The source of my metrics went down during app development,
underscoring the need for monitoring.
Currently if the app hits any kind of HTTP error on request for
new metrics it will raise a fatal error.
I could make it so that I'm emailed or otherwise notified when this happens...
But I didn't.

Another class of failure that is possible is that the metrics service
responds with a 200, but reports bad data (all 0's or nulls or something).
I suppose if I was motivated I could develop and install data quality monitoring and
alerting mechanism. If only there was already some product for that...

### Adding tests

Obviously better test coverage would have been better.
It was way easier than I expected to set up an environment
suitable for integration tests in Github Actions.
I followed [these instructions](https://docs.github.com/en/free-pro-team@latest/actions/guides/creating-postgresql-service-containers)
to set up a postgres database to make it available for my tests suite.
Now I have a fair amount of integration test coverage as well.

# Crypto Metrics Tracker

Welcome to the Crypto-Metrics tracker!
This is a toy app designed to track Crypto metrics and send alerts based on simple thresholds.

## Usage

Each minute the app collects the latest metrics from
[livecoin's ticker](https://api.livecoin.net/exchange/ticker).
It stores those metrics in a database,
and then compares the latest metrics with the averages over the last 24 hours.

You can have the app notify you when a metric value exceeds 3x the 24 hr rolling average.

You can also query the app for historical metrics.

### Email: /emails

Sign up for email alerts with a post request:

```Shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"address":"your_email@email.com"}' \
  ${API_BASE}/emails
```

Remove your email with a DELETE:

```Shell
curl --header "Content-Type: application/json" \
  --request DELETE \
  --data '{"address":"your_email@email.com"}' \
  ${API_BASE}/emails
```

See what emails are in the list with a GET:

```Shell
curl ${API_BASE}/emails
```

### Metrics: /metrics and /list-metrics

Find the metrics and Symbols available with a GET to `/list-metrics`:

```Shell
curl ${API_BASE}/list-metrics
```

Get a graph of metric performance and rank of standard dev of
the metric against the same metric of other symbols with a GET to `/metrics`:

```Shell
curl ${API_BASE}/metrics?metric=${your_metric}&symbol=${your_symbol}
```

## Local Dev

To set up a local environment do the following:

- copy .env.example to .env `cp .env.example .env`
- fill out the .env file with your app's parameters.
- run `docker-compose up -d` to start a postgres DB in the background
- activate your virtual env and install requirements
- hack away

I've included `if __name__ == '__main__' ... ` blocks in each of the
files for the lambda functions.
This way you can invoke your code locally from the terminal if you want.

## Deploying to production

The app is made up of 2 lambda functions behind an API gateway,
and 1 lambda function running on a timer.

When deploying your code to master (actually any branch), a Github Actions workflow
will package up your code and deploy it to S3 where it is used
to update the three lambda functions.

## Creating infra with Terraform

Use the terraform files to generate the following ifra:
- a postgres database and VPC etc
- the lambda functions and permissions
- API gateway stuff

## Run tests

I use pytest to run the test suite.
Activate your virtual env and then run the tests with: `pytest`.
If you haven't already installed the package itself into your virtual env
then you will have to run: `pip install -e .`.
Do this if pytest can't find your code.

## Productionizing

More to come on this! I should talk about:

- storing more metrics than what I have currently
- querying metrics more often
- efficiency of checking for anomolies
- DB performance for STDev's and AVG's
- maybe use a streaming/windowing solution?

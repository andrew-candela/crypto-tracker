# Crypto Metrics Tracker

Welcome to the Crypto-Metrics tracker!
This is a toy app designed to track Crypto metrics and send alerts based on simple thresholds.
It's also a fun excuse to get some experience with AWS's API Gateway.

The app itself consists of two lambda functions running behind an API gateway.
There is a third lambda function running on a 5 minute timer to collect data.
I use a Postgres RDS for the storage layer.

The `terraform/` folder has all of the configuration needed to run the app in your own account.

This app costs me about $0.50 to run per day.
Most of that spend is due to the `db.t2.micro` RDS instance.
While I was working on this, the price of Bitcoin on the Livecoin exchange fluctuated wildly.
It rose about 10x over current market rates, probably due to malicious activity.
It just goes to show what potential an app like this has.
If you're a savvy bitcoin trader, this project could be quite useful for you!

### A note about LiveCoin and CryptoWatch

This project originally used LiveCoin to gather crypto metrics.
Some bad actors made it into Livecoin's systems and
[caused some problems](https://www.zdnet.com/article/russian-crypto-exchange-livecoin-hacked-after-it-lost-control-of-its-servers/#ftag=RSSbaffb68).
They drove up the bitcoin price to about 10x higher than it should have been,
and then presumably liquidated their assets with the inflated price.
These events definitely make this project seem appropriate.
Anyway, this has resulted in removal of LiveCoin's public API.
I've settled on useng CryptoWatch instead.

## Usage

Every 5 minutes the app collects the latest metrics from
[CryptoWatch's API](https://docs.cryptowat.ch/rest-api/).
Right now the only metric I collect is `price`.
The app stores those metrics in a database,
and then compares the latest metrics with the averages over the last 24 hours.

You can have the app notify you when a metric value exceeds `ALERT_THRESHOLD`x the 24 hr rolling average.
You can set `ALERT_THRESHOLD` in your .env file.
I moved this from `3` to `10` because this can get noisy.

You can also query the app for historical metrics.

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

To set up a local environment you must do the following:

- copy .env.example to .env `cp .env.example .env`
- fill out the .env file with your app's parameters. `PG_HOST` should be `localhost` in this case.
- run `docker-compose up -d` to start a postgres DB in the background
- activate your virtual env and install requirements
- install this python package itself: `pip install -e .`
- run the migration script to create the tables in the DB: `python scripts/run_migrations.py`
- hack away

## Deploying to production

The app is made up of 2 lambda functions behind an API gateway,
and 1 lambda function running on a timer.

When deploying your code to master (actually any branch), a Github Actions workflow
will package up your code and deploy it to S3 where it is used
to update the three lambda functions.
You'll have to add some secrets to your github repo in order for this step to work
with your own AWS account.

If you're trying to deploy your code but you haven't yet created the lambda functions,
then the deploymennt pipleing will fail.
If this happens, follow the steps to create the needed AWS infra with Terraform below.

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
If you find that pytest can't find the `service` package, this is probably the reason.

## Productionizing

I've taken a lot of shortcuts to get this to work.
If you're going to make a project like this production ready, I'd suggest
using a framework like Django.

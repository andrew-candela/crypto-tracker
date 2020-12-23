Welcome to the Crypto-Metrics tracker!

This is a toy app designed to track Crypto metrics and send alerts based on simple thresholds.

# Usage
The app collects metrics every minute and allows for querying metrics.

## Sign up for email alerts
Coming soon!

## Query Metrics
Coming soon!

# Local Dev
To set up a local environment do the following:
- fill out the .env vile from the .env.example
- run `docker-compose up -d` to start postgres locally
- activate your virtual env and install requirements
- hack away

# deploy to production
The app is a series of lambda functions behind an API gateway.

## Creating infra with Terraform
Use the terraform files to generate the following ifra:
- a postgres database and VPC etc
- the lambda functions and permissions
- API gateway stuff

## Deploying code package to lambda
Set this up with github actions

# Run tests
Use Pytest. More to come soon!

# Productionizing
More to come on this! I should talk about:
- storing more metrics than what I have currently
- querying metrics more often
- efficiency of checking for anomolies
- DB performance for STDev's and AVG's
- maybe use a streaming/windowing solution?

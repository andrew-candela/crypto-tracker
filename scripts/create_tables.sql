CREATE SCHEMA IF NOT EXISTS crypto;

-- this resolves requirement #1
-- a scheduled job will run to populate this table

-- I guess I'll also just query this table directly 
-- to satisfy requirements #2 and #3
-- DROP TABLE IF EXISTS crypto.currency_stats;
CREATE TABLE IF NOT EXISTS crypto.currency_stats (
    "market_symbol_combo" varchar(250),
    "price" float,
    "poll_time" timestamp with time zone default current_timestamp
);

CREATE INDEX IF NOT EXISTS currency_stat_date 
ON crypto.currency_stats (market_symbol_combo, poll_time);

DROP TABLE IF EXISTS crypto.email_recipients;
CREATE TABLE IF NOT EXISTS crypto.email_recipients (
    "address" varchar(250) primary key
);

DROP MATERIALIZED VIEW IF EXISTS last_days_standard_deviation;
CREATE MATERIALIZED VIEW last_days_standard_deviation AS 
SELECT
    market_symbol_combo as dimension,
    stddev(price) as price_stddev
FROM
    crypto.currency_stats
WHERE
    poll_time >= NOW() - '1 DAY'::interval
GROUP BY
    market_symbol_combo
having stddev(price) is not null
;

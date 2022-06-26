# download-from-common-crawl

This project uses Terraform to schedule Athena Queries
in AWS us-east-1 querying the [Common Crawl](https://commoncrawl.org/),
which contains petabytes of billions of webpages in 40+ languages.

This project was designed to run for free on us-east-1 where
the data is located.

# development

1. run `deploy.sh dev`
2. wait for the athena table to be created
3. run `MSCK REPAIR TABLE ccindex`
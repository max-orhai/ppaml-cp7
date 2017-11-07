#!/bin/bash

for fips in $(ls ../data/weather | cut -c 1-5)
do
    curl "https://flu-vaccination-map.hhs.gov/api/v1/counties.json?fips_id=${fips}&medicare_status=A" | jq '.results|map({medicare_status, year, week, week_start, count, percentage})' > vaccinations/$fips.json
    curl "https://flu-vaccination-map.hhs.gov/api/v1/counties.json?fips_id=${fips}&medicare_status=O" | jq '.results|map({medicare_status, year, week, week_start, count, percentage})' >> vaccinations/$fips.json
done

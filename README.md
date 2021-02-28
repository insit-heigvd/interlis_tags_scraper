# Interlis tags scraper

This script is intended to extract tags keys and values from all interlis model
files hosted on https://models.geo.admin.ch/

## Requirements
Docker version 20.10.4    
docker-compose version 1.27.4    

## Quick start

1. Clone this repo
```
git clone git@github.com:insit-heigvd/interlis_tags_scraper.git \
  && cd ./interlis_tags_scraper \
  && mkdir output
```

2. Start and log the app
```
docker-compose up -d && docker-compose logs -f
```

3. Enjoy results in `./output/`

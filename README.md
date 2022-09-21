#  eBay-Image-Scraper

A quick and dirty tool for downloading all images found on an eBay page. I made it to automate some archiving work I'm doing. I'll eventually expand the tool to support other sites like Amazon, Taobao and WorthPoint in the future (in fact, it should work to a degree on any website), but right now, it's tailored for eBay.

## Install requirements

    pip3 install bs4 tldextract

## Running

    python .\main.py arg1 arg2 arg3

* arg1 (required): the URL
* arg2 (optional): scrape types (default 4, see below)
* arg3 (optional): find & delete duplicates (default 1 = on, 0 = off)

## Scrape types

* 1: Look for images in HTML only
* 2: Look in CSS for images
* 3: Look in JavaScript for images (not yet implemented)
* 4: All of the above 
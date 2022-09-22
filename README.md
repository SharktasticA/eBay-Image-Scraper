#  eBay-Image-Scraper

A quick and dirty tool for downloading all images found on an eBay page. I made it to automate some archiving work I'm doing, hence designed as a class I can use in various other applications I'm developing. I'll eventually expand the tool to support other sites like Amazon, Taobao and WorthPoint in the future (in fact, it should work to a degree on any website), but right now, it's tailored for eBay.

## Install requirements

    pip3 install bs4 tldextract

__Note:__ During development, I'm also using the `var_dump` package for debugging. You can remove the `var_dump` import in `scraper.py` or also install this package to proceed.

## Running

`main.py` is a given ready-to-use driver for the `Scraper` class.

    python .\main.py arg1 arg2 arg3 arg4

* arg1 (required): the URL
* arg2 (optional): scrape types (default 4, see below)
* arg3 (optional): find & delete duplicates (default 1 = on, 0 = off)
* arg4 (optional): enable site-specific optimisations (default 1 = on, 0 = off)

## Scrape types

* 1: Look for images in HTML only
* 2: Look for images in CSS only
* 3: Look for images in JavaScript only
* 4: Look for images in HTML, CSS and JavaScript 
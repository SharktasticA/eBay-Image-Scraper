import random
import re
import string
import requests
import os
from var_dump import var_dump
from datetime import datetime
from bs4 import BeautifulSoup
import tldextract

curdir = os.getcwd()
curdir = os.path.join(curdir, "scrapes")
if not os.path.exists(curdir):
    os.makedirs(curdir)

site = 'https://www.ebay.com/itm/185564756547?nma=true&si=vcasXQrOUbekuNb6jRl%252FCLxcix8%253D&orig_cvip=true&nordt=true&rt=nc&_trksid=p2047675.l2557'
site_info = tldextract.extract(site)

response = requests.get(site)

soup = BeautifulSoup(response.text, 'html.parser')
img_tags = soup.find_all('img')

urls = [img['src'] for img in img_tags]

if len(urls) > 0:
    newdir = os.path.join(curdir, datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + site_info.domain)
    os.makedirs(newdir)

    for url in urls:
        filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png))$', url)
        if not filen:
            print("Skipping " + format(url) + " due to lack of compatible image found")
            continue

        if os.path.exists(os.path.join(newdir, filen.group(1))):
            print("Image with this filename already exists, appending random str to new file filename...")
            to_append = ''.join(random.choice(string.ascii_letters) for i in range(4))
            with open(os.path.join(newdir, to_append + filen.group(1)), 'wb') as f:
                if 'http' not in url:
                    # Handle relative image links
                    url = '{}{}'.format(site, url)
                response = requests.get(url)
                f.write(response.content)
        else:
            with open(os.path.join(newdir, filen.group(1)), 'wb') as f:
                if 'http' not in url:
                    # Handle relative image links
                    url = '{}{}'.format(site, url)
                response = requests.get(url)
                f.write(response.content)

else:
    print("No valid images found on page")
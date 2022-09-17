import random
import re
import string
import requests
import os
from var_dump import var_dump
from datetime import datetime
from bs4 import BeautifulSoup
import tldextract

# Prepare directory for all downloads
curdir = os.getcwd()
curdir = os.path.join(curdir, "scrapes")
if not os.path.exists(curdir):
    os.makedirs(curdir)

# Setup site info
site = 'https://www.ebay.com/itm/185564756547?nma=true&si=vcasXQrOUbekuNb6jRl%252FCLxcix8%253D&orig_cvip=true&nordt=true&rt=nc&_trksid=p2047675.l2557'
site_info = tldextract.extract(site)
response = requests.get(site)
soup = BeautifulSoup(response.text, 'html.parser')

# Prepare directory for this session's downloads
newdir = os.path.join(curdir, datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + site_info.domain)
os.makedirs(newdir)

# 'Surface-level' (HTML) sweep
img_tags = soup.find_all('img')
urls = [img['src'] for img in img_tags]

if len(urls) > 0:

    for url in urls:
        filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png|svg))$', url)
        if not filen:
            print("Skipping " + format(url) + " due to lack of compatible image found")
            continue

        if os.path.exists(os.path.join(newdir, "html_" + filen.group(1))):
            print("Image with this filename already exists, appending random str to new file filename...")
            to_append = ''.join(random.choice(string.ascii_letters) for i in range(4))
            with open(os.path.join(newdir, "html_" + to_append + "_" + filen.group(1)), 'wb') as f:
                if 'http' not in url:
                    # Handle relative image links
                    url = '{}{}'.format(site, url)
                response = requests.get(url)
                f.write(response.content)
        else:
            with open(os.path.join(newdir, "html_" + filen.group(1)), 'wb') as f:
                if 'http' not in url:
                    # Handle relative image links
                    url = '{}{}'.format(site, url)
                response = requests.get(url)
                f.write(response.content)

else:
    print("No images found with HTML sweep")

# CSS level sweep
link_tags = soup.find_all('link')
urls = [link['href'] for link in link_tags]

if len(urls) > 0:
    for url in urls:
        if ".css" in url:
            css_resp = requests.get(url)
            css_txt = str(css_resp.text)

            # Look for any background URLs
            bg_urls = re.findall(r'background:url\((.*?)\)', css_txt)
            # Look for any background images
            bg_imgs = re.findall(r'background-image:url\((.*?)\)', css_txt)
            
            imgs = bg_urls + bg_imgs
            for url in imgs:
                filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png|svg))$', url)
                if not filen:
                    print("Skipping " + format(url) + " due to lack of compatible image found")
                    continue

                if os.path.exists(os.path.join(newdir, "css_" + filen.group(1))):
                    print("Image with this filename already exists, appending random str to new file filename...")
                    to_append = ''.join(random.choice(string.ascii_letters) for i in range(4))
                    with open(os.path.join(newdir, "css_" + to_append + "_" + filen.group(1)), 'wb') as f:
                        if 'http' not in url:
                            # Handle relative image links
                            url = '{}{}'.format(site, url)
                        response = requests.get(url)
                        f.write(response.content)
                else:
                    with open(os.path.join(newdir, "css_" + filen.group(1)), 'wb') as f:
                        if 'http' not in url:
                            # Handle relative image links
                            url = '{}{}'.format(site, url)
                        response = requests.get(url)
                        f.write(response.content)
else:
    print("No CSS file links found to complete CSS sweep")
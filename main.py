from filecmp import cmp
from pathlib import Path
import random
import re
import string
import requests
import os
from var_dump import var_dump
from datetime import datetime
from bs4 import BeautifulSoup
import tldextract
import sys

# Prepare directory for all downloads
curdir = os.getcwd()
curdir = os.path.join(curdir, "scrapes")
if not os.path.exists(curdir):
    os.makedirs(curdir)

# Get arguments
args = sys.argv
args_c = len(args) - 1
site = ""
option = 3
remove_dups = True
if args_c == 0:
    print("ERROR: no URL given")
    exit()
if args_c > 0:
    site = args[1]
if args_c > 1:
    option = int(args[2])
if args_c > 2:
    remove_dups = bool(int(args[3]))

# Setup site info
site_info = tldextract.extract(site)
response = requests.get(site)
soup = BeautifulSoup(response.text, 'html.parser')

# Prepare directory for this session's downloads
newdir = os.path.join(curdir, datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + site_info.domain)
os.makedirs(newdir)
newpath = Path(newdir)

# 'Surface-level' (HTML) sweep
img_tags = soup.find_all('img')
urls = []
for img in img_tags:
    if img.has_key("src"):
        urls.append(img["src"])

possible_ebay_fulls = []

if len(urls) > 0:
    for url in urls:
        filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png|svg))$', url)
        if not filen:
            print("Skipping " + str(url) + " due to lack of compatible image found")
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

        # Flag if URL is eBay image and should be checked again
        # for full-size version
        if "i.ebayimg.com/images/g/" in url:
            possible_ebay_fulls.append(url)

else:
    print("No images found with HTML sweep")

# Check any eBay URLs flagged for full-size check
if len(possible_ebay_fulls) > 0:
    for url in possible_ebay_fulls:
        url_comps = url.split('/')
        url_comps[6] = "s-l1600.jpg"
        test_url = "/".join(url_comps)

        filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png|svg))$', test_url)
        if not filen:
            print("Skipping " + str(test_url) + " due to lack of compatible image found")
            continue

        if os.path.exists(os.path.join(newdir, "full_" + filen.group(1))):
            print("Image with this filename already exists, appending random str to new file filename...")
            to_append = ''.join(random.choice(string.ascii_letters) for i in range(4))
            with open(os.path.join(newdir, "full_" + to_append + "_" + filen.group(1)), 'wb') as f:
                if 'http' not in test_url:
                    # Handle relative image links
                    test_url = '{}{}'.format(site, test_url)
                response = requests.get(test_url)
                f.write(response.content)
        else:
            with open(os.path.join(newdir, "full_" + filen.group(1)), 'wb') as f:
                if 'http' not in test_url:
                    # Handle relative image links
                    test_url = '{}{}'.format(site, test_url)
                response = requests.get(test_url)
                f.write(response.content)

# CSS level sweep
if option > 1:
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

# JS level sweep
# TODO
if option > 2:
    script_tags = soup.find_all('script')
    for script in script_tags:
        var_dump(script)
        exit()
        if "src" in script:
            var_dump(script)

# Remove duplicates if applicable
if remove_dups:
    files = sorted(os.listdir(newpath))
    dups = []

    for file in files:
        if_dup = False
  
        for class_ in dups:
            if_dup = cmp(newpath / file, newpath / class_[0], shallow=False)

            if if_dup:
                class_.append(file)
                break
    
        if not if_dup:
            dups.append([file])

    for dup in dups:
        dup_c = len(dup)
        if dup_c > 1:
            for i in range(dup_c - 1):
                print("Removing duplicate " + dup[i])
                os.remove(os.path.join(newdir, dup[i]))
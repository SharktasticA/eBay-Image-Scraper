from filecmp import cmp
from pathlib import Path
import random
import re
import string
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup
import tldextract
from time import sleep

# Following to be removed after all development:
from var_dump import var_dump

class Archiver:
    # Possible user agent strings to use
    agents = [ "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42" ]

    # Options
    site = ""
    option = 4
    removedups = True
    sspecific = True

    # Environment
    curdir = None
    newdir = None
    newpath = None
    soup = None
    
    # Make random header for use with requests.get()
    def __random_header(self):
        random_user_agent = random.choice(self.agents)
        sleep(random.uniform(0, 0.1))
        return { 'User-Agent': random_user_agent }

    def __setup_environment(self):
        # Prepare directory for all downloads
        self.curdir = os.getcwd()
        self.curdir = os.path.join(self.curdir, "scrapes")
        if not os.path.exists(self.curdir):
            os.makedirs(self.curdir)

        # Setup site info
        site_info = tldextract.extract(self.site)
        response = requests.get(self.site, headers=self.__random_header())
        self.soup = BeautifulSoup(response.text, 'html.parser')

        # Prepare directory for this session's downloads
        self.newdir = os.path.join(self.curdir, datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + site_info.domain)
        os.makedirs(self.newdir)
        self.newpath = Path(self.newdir)

    def __init__(self, site, option = 4, removedups = True, sspecific = True):
        self.site = site
        self.option = option
        self.removedups = True
        self.sspecific = True
        self.__setup_environment()

    # HTML level scrape
    def __html_scrape(self):
        img_tags = self.soup.find_all('img')
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

                if os.path.exists(os.path.join(self.newdir, "html_" + filen.group(1))):
                    print("Image with this filename already exists, appending random str to new file filename...")
                    to_append = ''.join(random.choice(string.ascii_letters) for i in range(4))
                    with open(os.path.join(self.newdir, "html_" + to_append + "_" + filen.group(1)), 'wb') as f:
                        if 'http' not in url:
                            # Handle relative image links
                            url = '{}{}'.format(self.site, url)
                        response = requests.get(url, headers=self.__random_header())
                        f.write(response.content)
                else:
                    with open(os.path.join(self.newdir, "html_" + filen.group(1)), 'wb') as f:
                        if 'http' not in url:
                            # Handle relative image links
                            url = '{}{}'.format(self.site, url)
                        response = requests.get(url, headers=self.__random_header())
                        f.write(response.content)

                # Site-specific code: Flag if URL is eBay image and should be
                # checked again for full-size version
                if "i.ebayimg.com/images/g/" in url and self.sspecific == True:
                    possible_ebay_fulls.append(url)
        else:
            print("No images found with HTML sweep")

        # Site-specific code: Check any eBay URLs flagged for
        # full-size check
        if len(possible_ebay_fulls) > 0 and self.sspecific == True:
            for url in possible_ebay_fulls:
                # Rebuild the URL to likely full-size image URL
                # Note "s-l1600" is the usual filename for large eBay images
                url_comps = url.split('/')
                url_comps[6] = "s-l1600.jpg"
                test_url = "/".join(url_comps)

                filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png|svg))$', test_url)
                if not filen:
                    print("Skipping " + str(test_url) + " due to lack of compatible image found")
                    continue

                if os.path.exists(os.path.join(self.newdir, "full_" + filen.group(1))):
                    print("Image with this filename already exists, appending random str to new file filename...")
                    to_append = ''.join(random.choice(string.ascii_letters) for i in range(4))
                    with open(os.path.join(self.newdir, "full_" + to_append + "_" + filen.group(1)), 'wb') as f:
                        if 'http' not in test_url:
                            # Handle relative image links
                            test_url = '{}{}'.format(self.site, test_url)
                        response = requests.get(test_url, headers=self.__random_header())
                        f.write(response.content)
                else:
                    with open(os.path.join(self.newdir, "full_" + filen.group(1)), 'wb') as f:
                        if 'http' not in test_url:
                            # Handle relative image links
                            test_url = '{}{}'.format(self.site, test_url)
                        response = requests.get(test_url, headers=self.__random_header())
                        f.write(response.content)

    # CSS level sweep
    def __css_scrape(self):
        link_tags = self.soup.find_all('link')
        urls = [link['href'] for link in link_tags]

        if len(urls) > 0:
            for url in urls:
                if ".css" in url:
                    css_resp = requests.get(url, headers=self.__random_header())
                    css_txt = str(css_resp.text)

                    # Look for any background URLs
                    bg_urls = re.findall(r'background:url\((.*?)\)', css_txt)
                    # Look for any background images
                    bg_imgs = re.findall(r'background-image:url\((.*?)\)', css_txt)
                    
                    imgs = bg_urls + bg_imgs
                    for iurl in imgs:
                        if iurl[:2] == "//":
                            iurl = "https:" + iurl

                        filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png|svg))$', iurl)
                        if not filen:
                            print("Skipping " + format(iurl) + " due to lack of compatible image found")
                            continue

                        if os.path.exists(os.path.join(self.newdir, "css_" + filen.group(1))):
                            print("Image with this filename already exists, skipping...")
                            continue
                        else:
                            with open(os.path.join(self.newdir, "css_" + filen.group(1)), 'wb') as f:
                                if 'http' not in iurl:
                                    # Handle relative image links
                                    url = '{}{}'.format(self.site, url)
                                response = requests.get(iurl, headers=self.__random_header())
                                f.write(response.content)
        else:
            print("No CSS file links found to complete CSS sweep")

    # JS level sweep
    # TODO: implement inline JS checking
    def __js_scrape(self):
        script_tags = self.soup.find_all('script')
        urls = []
        for script in script_tags:
            if script.has_key("src"):
                if script["src"][:2] == "//":
                    urls.append("https:" + script["src"])
                else:  
                    urls.append(script["src"])

        if len(urls) > 0:
            for url in urls:
                js_resp = requests.get(url, headers=self.__random_header())
                js_txt = str(js_resp.text)

                imgs = re.findall("(https?:\/\/.*\.(?:jpg|jpeg|webp|gif|png|svg))", js_txt)
                for iurl in imgs:
                    filen = re.search(r'/([\w_-]+[.](jpg|jpeg|webp|gif|png|svg))$', iurl)
                    if not filen:
                        print("Skipping " + format(iurl) + " due to lack of compatible image found")
                        continue

                    if os.path.exists(os.path.join(self.newdir, "js_" + filen.group(1))):
                        print("Image with this filename already exists, appending random str to new file filename...")
                        to_append = ''.join(random.choice(string.ascii_letters) for i in range(4))
                        with open(os.path.join(self.newdir, "js_" + to_append + "_" + filen.group(1)), 'wb') as f:
                            if 'http' not in iurl:
                                # Handle relative image links
                                url = '{}{}'.format(self.site, url)
                            response = requests.get(iurl, headers=self.__random_header())
                            f.write(response.content)
                    else:
                        with open(os.path.join(self.newdir, "js_" + filen.group(1)), 'wb') as f:
                            if 'http' not in iurl:
                                # Handle relative image links
                                url = '{}{}'.format(self.site, url)
                            response = requests.get(iurl, headers=self.__random_header())
                            f.write(response.content)  
        else:
            print("No images found with JS sweep")

    # Remove duplicates if applicable
    def __remove_dups(self):
        files = sorted(os.listdir(self.newpath))
        dups = []

        for file in files:
            if_dup = False
    
            for class_ in dups:
                if_dup = cmp(self.newpath / file, self.newpath / class_[0], shallow=False)

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
                    os.remove(os.path.join(self.newdir, dup[i]))

    # Run archiver
    def run(self):
        if self.option == 1 or self.option == 4:
            self.__html_scrape()
        if self.option == 2 or self.option == 4:
            self.__css_scrape()
        if self.option == 3 or self.option == 4:
            self.__js_scrape()
        if self.removedups:
            self.__remove_dups()

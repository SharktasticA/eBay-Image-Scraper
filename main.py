import sys
from scraper import *

args = sys.argv
args_c = len(args) - 1
site = ""
option = 4
removedups = True
sspecific = True

if args_c == 0:
    print("ERROR: no URL given")
    exit()
if args_c > 0:
    site = args[1]
if args_c > 1:
    option = int(args[2])
if args_c > 2:
    removedups = bool(int(args[3]))
if args_c > 3:
    sspecific = bool(int(args[4]))

scraper = Scraper(site, option, removedups, sspecific)
scraper.run()
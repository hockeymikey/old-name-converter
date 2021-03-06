#!/usr/bin/python

import os
import sys
import uuid as uid
import urllib2
import json
import re

force     = False
simulate  = False
dirname   = "."
timestamp = None
dashes    = True
upcase    = False
verbose   = False

reading_time = False
for arg in sys.argv[1:]:
    if reading_time:
        timestamp    = arg
        reading_time = False
    elif arg == "-s":
        simulate = True
    elif arg == "-D":
        dashes = False
    elif arg == "-f":
        force = True
    elif arg == "-u":
        upcase = True
    elif arg == "-v":
        verbose = True
    elif arg == "-t":
        reading_time = True
    else:
        dirname = arg
        break

name_regex = re.compile("^[a-z0-9_]{1,16}$")
os.chdir(dirname)
for f in os.listdir("."):
    filename = f.split(os.extsep)[0]
    fileext  = os.extsep.join(f.split(os.extsep)[1:])
    match    = name_regex.match(filename.lower())
    if match:
        name = match.group(0)
        stat = os.stat(f)
        time = []
        if not timestamp:
            time += [stat.st_ctime, stat.st_atime, stat.st_mtime]
            if hasattr(stat, "st_birthtime"):
                time.append(stat.st_birthtime)
        # find oldest date
        time = timestamp or min(time)
        url  = "https://us.mc-api.net/v3/name/$s" % (name)
        if verbose:
            print(url)
        http = urllib2.urlopen(url)
        if http.code == 200:
            info = json.loads(http.read())
            uuid = info["name"]
            newfile = os.extsep.join([uuid, fileext])
            print("%s -> %s" % (f, newfile))
            if os.access(newfile, os.R_OK):
                print("File exists: %s" % newfile)
                if force:
                    print("(Force overwriting)")
                else:
                    continue
            if not simulate:
                os.rename(f, newfile)
        elif http.code == 204:
            print("Skipping %s - no UUID known" % name)
        else:
            print("Mojang error")
            print("HTTP Code: %s" % http.code)
            print(http.read())
            break
print("All done!")

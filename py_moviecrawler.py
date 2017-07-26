#Author: twoDarkMessiah (twoDarkMessiah@gmail.com)
#Version: 0.1.0
#Date: 2017-07-26 23:50
#License: GPL 3

import urllib
import re
import argparse
import multiprocessing as mp
from urllib import request
from urllib.parse import urlencode
import os

def findLink(movie):
    print("Searching for: " + movie.strip())
    if (len(movie) < 4):
        if (len(movie) > 0):
            print("Title to short: " + movie + ". SKIP!")
        return None
    title = urllib.parse.quote(movie.strip())
    resource = urllib.request.urlopen("https://warez-heaven.ws/suche/?post_type=post&s=" + title)
    content = resource.read().decode(resource.headers.get_content_charset())
    lnum = 0
    ffound = 0
    for line in content.split("\n"):
        if ('<h4 class="news-teaser__headline">' in line):
            release = re.findall('<h4 class="news-teaser__headline">.{0,999}</h4>', line)[0]
            release.strip()
            release = release[34:-5]
            if "1080p" in line and "XXX" not in line:
                ffound = 1
        if ffound == 1 and ('Uploaded.net' in line or 'Share-Online.biz' in line) and 'filecrypt.cc' in line:
            link = re.findall('http.{1,99}html', line.replace("\n", " "))[0]
            print("Found link for '" + release + "': " + link)
            return (link, movie)
        lnum = lnum + 1
    return (None, movie)

def main():
    movies = []
    movies_found = []
    movies_missing = []
    args = None
    file_out = None
    file_missing = None

    parser = argparse.ArgumentParser(prog='main.py')
    parser.add_argument("file", help='specifay source file for movies')
    parser.add_argument("-o", "--output", help='file to save filecrypt links')
    parser.add_argument("-m", "--missing", help='file to save missing (failed) movies')
    parser.add_argument("-t", "--threads", help="how much threads should be used (default: 4)", default=4)
    args = parser.parse_args()

    if(not (os.path.isfile(args.file))):
        print("File '" + args.file + "' does not exits. Abort!" )
        return

    for line in open(args.file, 'r', encoding="utf-8"):
        movies.append(line)

    print (str(len(movies)) + " movies in list")
    print ("using " + args.threads + " threads")

    pool = mp.Pool(processes=int(args.threads))
    results = pool.map(findLink, movies);

    if (len(movies) > 0):
        if (not (args.output == None)):
            file_out = open(args.output, 'w')

    if (args.missing != None):
        fh_missing = open(args.missing, 'w', encoding="utf-8")

    for result in results:
        if(result[0] != None):
            movies_found.append(result[1])
            if(file_out != None):
                file_out.write(result[0] + "\r\n")
        else:
            movies_missing.append(result[1])
            if(fh_missing != None):
                fh_missing.write(result[1] + "\r\n")
        print (result[0])

    if(file_out != None):
        file_out.close()
    if(file_missing != None):
        file_missing.close()

    print("Links to " + str(len(movies_found)) + " from " + str(len(movies)) + " where found!")

if __name__ == "__main__":
    main()
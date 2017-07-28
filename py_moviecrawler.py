#Author: twoDarkMessiah (twoDarkMessiah@gmail.com)
#Version: 0.2.0
#Date: 2017-07-29 0:15
#License: GPL 3

import urllib
import re
import argparse
import multiprocessing as mp
from urllib import request
from urllib import parse
import os
import lxml.html
from pip._vendor import requests

#set allowed OCHs
allowed_hoster = ["Uploaded.net", "Share-online.biz"]

def findLink(movie):
    print("Searching for: " + movie.strip())
    if (len(movie) < 4):
        if (len(movie) > 0):
            print("Title to short: " + movie + ". SKIP!")
        return None
    title = urllib.parse.quote(movie.strip())
    resource = urllib.request.urlopen("https://warez-heaven.ws/suche/?post_type=post&s=" + title)
    content = resource.read().decode(resource.headers.get_content_charset())

    page = lxml.html.fromstring(content)
    elms = page.xpath("//div[@class='flag__body']")
    release_list = []
    for elm in elms:
        title = ""
        release = ""
        size = 0.0
        links = []
        info_link = None
        for child in elm.getchildren():
            if(child.tag is not None):
                 if(child.tag == "h4" and child.text is not None):
                     release = child.text
                     tvshow = len(re.findall('S\d{2}', release))
                     if not("1080p" in release and "XXX" not in release and '3D' not in release and tvshow == 0):
                         release = ""
                 if (child.tag == "span" and child.text is not None):
                    sizes = re.findall("\d{1,2}\.{1}\d{2}\sGB", child.text)
                    if(len(sizes) > 0):
                        size = float(sizes[0].replace(" GB", ""))
                 if (child.tag == "h3" and child.text is not None):
                     title = child.text
                 if(child.tag == "a" and child.get("title") != None and child.get("title") in allowed_hoster and child.get("href") != None):
                     links.append((child.get("title"), child.get("href")))
                 if(child.tag == "a" and child.get("title") == "Warezkorb" and child.get("href") != None):
                     tmp_info_link = child.get("href")
                     re_result = re.findall("\d{6}", tmp_info_link)
                     if (len(re_result) > 0):
                         info_link = "https://warez-heaven.ws/" + str(re_result[0]) + "/"
        if(info_link != None):
            info_link = info_link + release
            if(title != "" and release != "" and size != 0.0 and len(links) > 0 and info_link != None):
                release_list.append((title, release, size, info_link, links))
    release_list = sorted(release_list, key=lambda release: release[2], reverse=True)

    for rel_info in release_list:
        resource_info = urllib.request.urlopen(rel_info[3])
        content_info = resource_info.read().decode(resource.headers.get_content_charset())
        page_info = lxml.html.fromstring(content_info)
        dl_btns = page_info.xpath("//a[@id='buttonnav']")
        for dl_btn in dl_btns:
            if(dl_btn.get("title") != None):
                hoster = dl_btn.get("title")
                status = False
                for dl_sub in dl_btn.getchildren():
                    if(dl_sub.tag == "img" and dl_sub.get("class") == "status_icon"):
                        status = ( dl_sub.get("title") == "Online" )
                for link in rel_info[4]:
                    if (link[0] == hoster):
                        if(status == True):
                            print ("Found release: " + rel_info[1] + " (" + str(rel_info[2]) + "GB) - " + hoster)
                            return (link[1], movie)
    return ( None, movie )

def moviedbsearch(title):
    url = "https://api.themoviedb.org/3/search/tv"
    payload = {'api_key': "<YOUR_API_KEY>", 'langauge': "de-DE", 'query': title}
    data = urllib.parse.urlencode(payload)
    data = data.encode('ascii')
    req = urllib.request.Request(url, data)
    res = urllib.request.urlopen(req)
    print (res.read())

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
        if(len(line.strip()) >= 4):
            movies.append(line)

    print (str(len(movies)) + " movies in list")
    print ("Using " + args.threads + " threads")
    if int(args.threads) > 8:
        print("Warning: more than 8 threads can lead to random crashes")

    pool = mp.Pool(processes=int(args.threads), maxtasksperchild=1)
    results = pool.map(findLink, movies)
    pool.close()

    if (len(movies) > 0):
        if (not (args.output == None)):
            file_out = open(args.output, 'w')

    fh_missing = None
    if (args.missing != None):
        fh_missing = open(args.missing, 'w', encoding="utf-8")

    for result in results:
        if(result[0] != None):
            movies_found.append(result[1])
            if(file_out != None):
                file_out.write(result[0].strip() + "\n")
        else:
            movies_missing.append(result[1])
            if(args.missing != fh_missing != None):
                fh_missing.write(result[1].strip() + "\n")

    if(file_out != None):
        file_out.close()
    if(file_missing != None):
        file_missing.close()

    print("Links to " + str(len(movies_found)) + " from " + str(len(movies)) + " where found!")

if __name__ == "__main__":
    main()
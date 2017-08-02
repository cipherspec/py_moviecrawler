#Author: twoDarkMessiah (twoDarkMessiah@gmail.com)
#Version: 0.4.0
#Date: 2017-08-02 01:48
#License: GPL 3

import urllib
import re
import argparse
import multiprocessing as mp
from urllib import request
from urllib import parse
import os
import lxml.html
import xml.etree.ElementTree as xml

#set allowed OCHs
allowed_hoster = ["Uploaded.net", "Share-online.biz"]

#Your Plex Data
#Finding Auth Token: https://support.plex.tv/hc/en-us/articles/204059436-Finding-an-authentication-token-X-Plex-Token
plex_url = "http://plex.example.com:32401"
plex_auth_token = "<YOUR-PLEX-TOKEN>"
plex_library_id = 2 #Your Movie Library
plex_use = False #True, to compare movielist with plex

def findAllMovies(page_number):
    results = []
    try:
        resource = urllib.request.urlopen("https://warez-heaven.ws/hauptkategorie/Full-HD/page/" + str(page_number))
        content = resource.read().decode(resource.headers.get_content_charset())
        page = lxml.html.fromstring(content)
        elms = page.xpath("//div[@class='flag__body']")
        for elm in elms:
            title = ""
            release = ""
            size = 0.0
            links = []
            info_link = None
            for child in elm.getchildren():
                if (child.tag is not None):
                    if (child.tag == "h4" and child.text is not None):
                        release = child.text
                        tvshow = len(re.findall('S\d{2}', release))
                        if not ("1080p" in release and "XXX" not in release and '3D' not in release and tvshow == 0):
                            release = ""
                    if (child.tag == "span" and child.text is not None):
                        sizes = re.findall("\d{1,2}\.{1}\d{2}\sGB", child.text)
                        if (len(sizes) > 0):
                            size = float(sizes[0].replace(" GB", ""))
                    if (child.tag == "h3" and child.text is not None):
                        title = child.text
                    if (child.tag == "a" and child.get("title") != None and child.get(
                            "title") in allowed_hoster and child.get("href") != None):
                        links.append((child.get("title"), child.get("href")))
                    if (child.tag == "a" and child.get("title") == "Warezkorb" and child.get("href") != None):
                        tmp_info_link = child.get("href")
                        re_result = re.findall("\d{5,6}", tmp_info_link)
                        if (len(re_result) > 0):
                            info_link = "https://warez-heaven.ws/" + str(re_result[0]) + "/"
            if (info_link != None):
                info_link = info_link + release
                if (title != "" and release != "" and size != 0.0 and len(links) > 0 and info_link != None):
                    results.append((title, release, size, info_link, links))
    except:
        print ("Error on Page:" + str(page_number))
    print (str(len(results)) + " results on page " + str(page_number))
    return results


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
                     re_result = re.findall("\d{5,6}", tmp_info_link)
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

def loadPlexMovies():
    request_url = plex_url + "/library/sections/" + str(plex_library_id) + "/all?X-Plex-Token=" + plex_auth_token
    resource = urllib.request.urlopen(request_url)
    content = resource.read().decode(resource.headers.get_content_charset())
    movie_list = []
    root = xml.fromstring(content)
    for child in root:
        if(child.tag == "Video" and child.get("title") != None):
            movie_list.append(child.get("title"))

    print ("Found " + str(len(movie_list)) + " movies on Plex")
    return movie_list

def moviedbsearch(title):
    url = "https://api.themoviedb.org/3/search/tv"
    payload = {'api_key': "<YOUR-API-KEY>", 'langauge': "de-DE", 'query': title}
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
    parser.add_argument("-i", "--input", help='specifay source file for movies')
    parser.add_argument("-o", "--output", help='file to save filecrypt links')
    parser.add_argument("-m", "--missing", help='file to save missing (failed) movies')
    parser.add_argument("-t", "--threads", help="how much threads should be used (default: 4)", default=4)
    parser.add_argument("-a", "--scrap-all", help="scrap all 1080p movies from W-H", dest="all", action='store_true')

    args = parser.parse_args()


    if(not args.all):
        if(args.input == None):
            print("You must either specify an input file, or scrap all with --scrap-all")
            return
        if(not (os.path.isfile(args.input))):
            print("File '" + args.input + "' does not exits. Abort!" )
            return

    plex_movies = []
    if(plex_use):
        plex_movies = loadPlexMovies()


    skip_plex = 0
    if(not args.all):
        for line in open(args.input, 'r', encoding="utf-8"):
            if(len(line.strip()) >= 4):
                if (line.strip() in plex_movies):
                    skip_plex = skip_plex + 1
                    print(line.strip())
                else:
                    movies.append(line.strip())

        print (str(len(movies)) + " movies in list")
        if(plex_use):
            print (str(skip_plex) + " movies skipped, they are already in Plex")
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
    else:
        file_out = None
        if (not (args.output == None)):
            file_out = open(args.output, 'w')
        base_url = "https://warez-heaven.ws/hauptkategorie/Full-HD"
        resource = urllib.request.urlopen(base_url)
        content = resource.read().decode(resource.headers.get_content_charset())
        site_count = int(re.findall("Seite\s\d{1}\svon\s\d{1,5}", content)[0].replace("Seite 1 von ", ""))
        print("Found " + str(site_count) + " pages to crawl, let's do the work :)")
        pool = mp.Pool(processes=int(args.threads), maxtasksperchild=1)
        results = pool.map(findAllMovies, range(1, site_count))
        movie_list = []
        pool.close()
        for result_set in results:
            for entry in result_set:
                if entry[0] not in movie_list:
                    if(len(entry[4]) > 0):
                        movie_list.append(entry[0])
                        file_out.write(entry[4][0][1] + "\n")
                        print("new link for: " + entry[1])
        if(file_out != None):
            file_out.close()
if __name__ == "__main__":
    main()

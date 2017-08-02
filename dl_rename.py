#Author: twoDarkMessiah (twoDarkMessiah@gmail.com)
#Version: 0.5.0 (part of py_moviecrawler)
#Date: 2017-08-02 06:00
#License: GPL 3

import re
import os
import traceback

badword_list= ["AC3", "DL", "DTS", "German"]

def doRenameS(movie_src):
    doRename(movie_src, movie_src)

def doRename(movie_src, movie_dest):
    for name in [i for i in os.listdir(movie_src)]:
        try:
            better_name = name.replace(".", " ")
            title = re.findall('.*\d{4}\s', better_name)
            year = re.findall('\s\d{4}\s', better_name)
            quali = re.findall('\d{4}p{1}', better_name)
            if(len(year) > 0 and len(title) > 0 and len(quali) > 0):
                better_name = str(title[0][:-5]).strip() + " " + str(year[0][1:-1]).strip() + " (" + str(quali[0]).strip() + ")"
            if(name != better_name):
                print("rename '" + name + "'" + " to '" + better_name + "'" )
                os.rename(movie_src + name, movie_dest + better_name)
        except Exception as e:
            print("error parsing "+ name)
            print(traceback.format_exc())
    return

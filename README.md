# py_moviecrawler
Simple multithreaded python movie crawler

Disclaimer: I'm not responsable for the use of this software. Check if downloading of movies is in accordance with the laws of your country!

Description:
Search for filecrypt links (ul, so) for movies from W-H. The best available releases are picked. 

Usage: main.py [-h] [-o OUTPUT] [-m MISSING] [-t THREADS] file

![Image](https://i.imgur.com/n0T4oXR.png)

Changelog:
0.1.0
* Initial Release

0.1.1
* bugfix multithreading
* bugfix empty line in ouput
* filter results including tv_shows

0.2.0
* extended html parsing
* using offline check from w-h
* prefer releases with higher quality

0.3.0
* added plex support
* bufix for five digits movie ids

0.4.0
* added option --scrap-all

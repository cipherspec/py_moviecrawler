# py_moviecrawler
Simple multithreaded python movie crawler

Disclaimer: I'm not responsable for the use of this software. Check if downloading of movies is in accordance with the laws of your country!

Description:
Search for filecrypt links (ul, so) for movies from W-H. The best available releases are picked. 

Usage: main.py [-h] [-o OUTPUT] [-m MISSING] [-t THREADS] file

positional arguments:
  file                  specifay source file for movies

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        file to save filecrypt links
  -m MISSING, --missing MISSING
                        file to save missing (failed) movies
  -t THREADS, --threads THREADS
                        how much threads should be used (default: 4)

![Image](https://github.com/twoDarkMessiah/py_moviecrawler/blob/master/py_moviecrawler.png?raw=true)

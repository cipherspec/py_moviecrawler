#Author: twoDarkMessiah (twoDarkMessiah@gmail.com)
#Version: 0.5.0 (part of py_moviecrawler)
#Date: 2017-08-02 06:00
#License: GPL 3

from time import sleep

import re
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def searchOnBoerse(user, pw, search_list, allowed_hoster):
    print("Loading webdriver for boerse.to")
    driver = webdriver.Firefox()
    link_list = []
    try:
        driver.get("https://boerse.to")
        driver.set_page_load_timeout(10)
        driver.implicitly_wait(10)
        sleep(5)  #5 seconds cloudflare
        login = driver.find_element_by_xpath('//*[@id="SignupButton"]/a')
        if (login != None and "Login" in login.text):
            login.click()
            sleep(1)
            driver.find_element_by_id("ctrl_remember").click()
            driver.find_element_by_id("LoginControl").send_keys(user)
            driver.find_element_by_id("ctrl_password").send_keys(pw)
            driver.find_element_by_xpath('//*[@id="login"]/div/dl[3]/dd/input').click()
        sleep(1)
        for movie in search_list:
            try:
                #tmp_fc_links = []
                driver.get("https://boerse.to")
                found = False
                qs = driver.find_element_by_id("QuickSearchQuery")
                qs.send_keys(movie)
                sleep(1)
                qs.send_keys(Keys.RETURN)
                driver.find_element_by_class_name("searchResultSummary") #implicit wait
                releases = driver.find_elements_by_xpath('//div/div/h3/a')
                url_list = []
                for release in releases:
                    if(len(release.text.strip()) > 0):
                        tvshow = len(re.findall('S\d{2}', release.text))
                        if("1080p" in release.text and tvshow == 0):
                            print ("Found release:" + release.text)
                            url_list.append(release.get_attribute("href"))
                for url in url_list:
                    if (found):
                        break
                    driver.get(url)
                    sleep(2)
                    posts = driver.find_elements_by_xpath('//*/div[2]/div[1]/article/blockquote/div[1]')
                    for post in posts:
                        if(found):
                            break
                        content = post.get_attribute('innerHTML')
                        if("Pass" in content or "Password" in content or "Passwort" in content):
                            if(not("kein Passwort" in content or "nopass" in content or "kein Password" in content or "no pass" in content)):
                                print("Cotainer proteced by password. skip!")
                                continue
                        for och in allowed_hoster:
                            if(och in content):
                                search_range = int(content.index(och))
                                search_content = content[search_range:]
                                fc_links = re.findall('https{0,1}:\/\/w{0,3}\.{0,1}filecrypt.cc\/Container\/[A-Za-z0-9]{1,20}.html', search_content)
                                if(len(fc_links) > 0):
                                    link_list.append(fc_links[0])
                                    print("Found link: " + fc_links[0])
                                    found = True
                                    break

            except:
                print("Error searching for " + movie)

    except:
        print ("FATAL ERROR")
    finally:
        driver.close()
    return link_list

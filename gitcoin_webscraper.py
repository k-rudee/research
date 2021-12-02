#packages for scraping 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.support.ui as ui
import requests
import re
import pymongo
import time

s = Service("/Users/rudee/Desktop/chromedriver")
driver = webdriver.Chrome(service=s)
# 
driver.get("https://gitcoin.co/grants/explorer/?page=1&limit=6&me=false&sort_option=weighted_shuffle&collection_id=false&network=mainnet&state=active&profile=false&sub_round_slug=false&collections_page=1&grant_regions=&grant_types=&grant_tags=&tenants=&idle=false&featured=true&tab=grants")
time.sleep(3)

def scroll(driver, timeout):
    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)


        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height

scroll(driver,8)

links = driver.find_elements_by_xpath('//h2[contains(@class, "font-subheader")]/a')
hrefs = []

print("number of grants: " + str(len(links)))
for link in links:
    hrefs.append(link.get_attribute("href"))
    print(link.get_attribute("href"))
    
#hrefs = hrefs[2:5]

hrefs2 = {}

def loadingscroll(driver, timeout):
    scroll_pause_time = timeout

    # Get scroll height 
    last_height = driver.execute_script("return document.body.scrollHeight")
    

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)
        
        # Click Load More 

        click_more = True
        while click_more:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn.btn-outline-primary.btn-sm.mt-n4.mb-4"))).click()
            
            break


        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height

    
cookies = driver.find_element_by_css_selector(".btn.btn-primary.font-body.text-capitalize.float-right")
cookies.click()

for href in hrefs:
    hrefs2[href] = []
    driver.get(href)
    time.sleep(3)
    driver.maximize_window()
    html = driver.page_source
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    activity_button = driver.find_element_by_xpath('//a[contains(@id, "__BVID__4___BV_tab_button__")]')
    activity_button.click()
    while True:
        scroll(driver, 7)
        break
    activitypage = driver.page_source
    file_ = open('page.html', 'w')
    file_.write(activitypage)
    file_.close()
   
    
    contributions_button = driver.find_element_by_xpath('//a[contains(@id, "__BVID__6___BV_tab_button__")]')
    contributions_button.click()
    time.sleep(3)
    while True:
        loadingscroll(driver,7)
        break
    contributionspage = driver.page_source
    file_ = open('page.html', 'w')
    file_.write(contributionspage)
    file_.close()


    rg_button = driver.find_element_by_xpath('//a[contains(@id, "__BVID__8___BV_tab_button__")]')
    rg_button.click()
    time.sleep(3)
    while True:
      loadingscroll(driver,7)
      break
    rgpage = driver.page_source
    file_ = open('page.html', 'w')
    file_.write(rgpage)
    file_.close()

    
    

  




   







    







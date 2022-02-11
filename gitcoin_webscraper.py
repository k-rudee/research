#packages for scraping 
import datetime
from pymongo.pool import _METADATA
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import contextlib
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.support.ui as ui
import urllib3
from bs4 import BeautifulSoup
import requests
import re
import pymongo 
from pymongo import MongoClient
import time
import lxml
import warnings
import re

warnings.filterwarnings("ignore", category=DeprecationWarning)

# setup webdriver and connect to website 
s = Service("/Users/rudee/Desktop/chromedriver")
driver = webdriver.Chrome(service=s)
driver.get("https://gitcoin.co/grants/explorer/?page=1&limit=6&me=false&sort_option=weighted_shuffle&collection_id=false&network=mainnet&state=active&profile=false&sub_round_slug=false&collections_page=1&grant_regions=&grant_types=&grant_tags=&tenants=&idle=false&featured=true&tab=grants")
time.sleep(3)

#pymongo setup
cluster = "mongodb+srv://k_rudee:D@cluster0.celrr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(cluster)
#print(client.list_database_names())
db = client.grants
#print(db.list_collection_names())
collection = db.meta 
collection2 = db.html
collection3 = db.grantList


hrefs = []
grantList = collection3.find()
for grant in grantList:
    hrefs.append(grant["Grant URL"])


#scrolling functions 1
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

#scrolling function 2 - unlimited scroll capability 
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
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn.btn-outline-primary.btn-sm.mt-n4.mb-4"))).click()
            break
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height

#scrolling function 3 - unlimited scroll capability with modification for related grants page 
def rgscroll(driver, timeout):
    scroll_pause_time = timeout
    # Get scroll height 
    last_height = driver.execute_script("return document.innerHTML") # <== returns doc html before 
    t_end = time.monotonic() + 100 * 1
    while time.monotonic() < t_end:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(scroll_pause_time)
        # Click Load More 
        click_more = True
        while click_more:
            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn.btn-outline-primary.btn-sm.mt-n4.mb-4"))).click()
            time.sleep(1)
            break
        # # Calculate new scroll height and compare with last scroll height
        # new_height = driver.execute_script("return document.documentElement.innerHTML") # <== returns doc html after scrolling
        # if new_height == last_height:
        #     # If heights are the same it will exit the function
        #     break
        # last_height = new_height
        
#scrapes activity page 
def scrapeactivity(doc):
    soup4 = BeautifulSoup(doc, 'html5lib')
    test = soup4.find_all("div", {"class": "activity_main pl-2 row bg_new_grant_contribution m-0"})
    ab = soup4.find_all("div", {"class": "col-10 col-sm-7 pl-3 activity_detail"})
    ab2 = soup4.find_all("div", {"class": "activity_main pl-2 row bg_new_grant_contribution m-0"})
    soup4status = soup4.find_all("div", {"class": "col-11 activity_comments_main pl-4 px-sm-3"})
    for block in test:
        activityuser = block.find("b").text # <== scrapes username 
        ac1 = block.find("span", {"class": "value_in_token"}) #scrapes <== scrapes amount contributed 
        if not ac1: # <== check for NoneType
            print('element not found')
            ac1 = 'no text'
        else:
            ac1 = ac1.text
        ac2 = block.find("span", {"class": "mr-2"}) 
        num1 = ac2.find("span", {"class": "grey"}).text # <== scrapes num views 
        tips = block.find("span", {"class": "amount grey"}).text # <== scrapes total tips
        likes = block.find("span", {"class": "num grey"}).text # <== scrapes num likes 
        comments = block.find("a", {"class":"comment_activity mr-2"}) 
        comments1 = comments.find("span", {"class": "num grey"}).text # <== scrapes num comments 
        for block in soup4status:
            status = block.find("div", {"class": "activity_comments_main_comment pt-1 pb-1"}).text.strip() # <== scrapes transaction 
        dict2 = {"Username": activityuser, "Contribution": ac1, "Num Views": num1, "Tips": tips, "Likes": likes, "Comments": comments1, "Status": status}
        print(dict2)

#scrapes contribution page 
def scrapecontributions(y):
    soup2 = BeautifulSoup(y, 'html5lib')                                
    meta11 = soup2.find_all("div", {"class": "container py-3"})
    dict1 = {}
    for each in meta11:
        v1 = each.find("div", {"class": "d-flex mr-2"})
        v2 = v1.find('a')
        v3 = v2['href']
        donorName = v3[9:]
        cname = each.find_all("div", {"class": "row"})[2].text.strip()
        x1 = each.find("div", {"class": "row justify-content-end text-secondary"}).get_text(strip=True)
        x11 = x1.replace("\n", "")
        cryptoamt = x11.replace(" ", "")
        x3 = each.find_all("div", {"class": "row justify-content-end text-secondary"})[1].text.strip()
        x31 = x3.replace("\n", "")
        usdvalue = x31.replace(" ", "")
        timed8 = each.find_all("div", {"class": "row"})[3].text.strip()
        dict1 = {"Contributer": cname, "Crypto": cryptoamt, "USD": usdvalue, "Time": timed8}
        print(dict1)

#scrapes related grants page 
def scraperg(z):
    soup3 = BeautifulSoup(z , 'html5lib')
    meta12 = soup3.find_all("div", {"class": "col-12 col-md-6 col-xl-4 mb-4 infinite-item grant-card"})
    for card in meta12:
        rgurl = card.find("a")
        url2 = ("https://gitcoin.co" + rgurl['href'])
        rgname = card.find("div", {"class": "card-body"})
        rgname2 = rgname.find("h5").text
        dict3 = {"Related Grant": rgname2, "URL": url2}
        print(dict3)

#scrapes home page 
def homescrape(soup):
    soup = BeautifulSoup(soup, 'html5lib')  
    meta1= soup.find("div", {"class": "mt-3 border-bottom"})
    gname = meta1.find("h2")
    #grant-subtags
    meta2= soup.find("div", {"class": "col-12 col-md-auto"})
    #url-tag
    meta3 = soup.find("div", {"class": "col-12 col-md-5 col-md-auto mb-3"})
    urltag = meta3.find("a")
    #ether-tag
    meta4 = soup.find("div", {"class": "col-12 col-md-5 col-md-auto mb-2"})
    ethertag = meta4.find("a")
    #twitter-tag
    meta5 = soup.find_all("div", {"class": "col-12 col-md-5 col-md-auto mb-3"})[1]
    twitter = meta5.find("a")
    #geo-tag
    meta6 = soup.find("span", {"class": "text-grey-400text-primary py-1 px-2 font-weight-normal mr-2"})
    geo = meta6.get_text().strip()
    #funding-tag
    meta8= soup.find("div", {"class": "col mb-5"})
    funding = meta8.find("h2")
    #grant-subtags
    tags = []
    for tag in meta2.findAll('a'):
        tags.append((tag.string.strip()))
    #gitcoin-url 
    meta9 = soup.find("div", {"class": "activity_detail_content font-body pb-2"})
    gitcoinurl = meta9.find("a")
    g2 = ("https://gitcoin.co" + gitcoinurl['href'])
    #about
    meta10 = soup.find("div", {"class": "ql-editor"})
    about = []
    for para in meta10.find_all('p'):
        if len(para.get_text(strip=True)) > 1:
            about.append((para.text.strip()))
    dict7 = {"Grant URL": urltag.get_text().strip(), "Ether-Addy": ethertag['href'],"Twitter": twitter['href'], "Geo-Location": geo, "Lifetime Funds": funding.text, "g-url": g2 }
    print(dict7)
    # print("URL: " + urltag.get_text().strip())
    # print("Ether-Addy: " +ethertag['href'])
    # print("Twitter: " + twitter['href'])
    # print("Geo-Location: " + geo)
    # print("Lifetime Funds: " + funding.text)
    # print ("g-url: " + g2)
    # time.sleep(5)

#contributions click
def csclick():
    contributions_button = driver.find_element_by_xpath('//a[contains(@id, "__BVID__9___BV_tab_button__")]')
    contributions_button.click()
    time.sleep(3)
    while True:
        loadingscroll(driver,7)
        break
    contributionspage = driver.page_source

#use to scroll to botttom of home page
#scroll(driver,6)

#locating grant-link using xpath
# links = driver.find_elements_by_xpath('//h2[contains(@class, "font-subheader")]/a')

#grant-links are stored in this hrefs list 
# hrefs = hrefs[0:5]

# print("number of grants: " + str(len(links)))
# for link in links:
#     hrefs.append(link.get_attribute("href"))
#     print(link.get_attribute("href"))

#cookies script 
cookies = driver.find_element_by_css_selector(".btn.btn-primary.font-body.text-capitalize.float-right")
cookies.click()

#uploading links to mongoDB 
#capture12 = {"Grant URL": hrefs}
#upload1 = collection3.insert_one(capture12)

#iterate through test pages
# hrefs = hrefs[2:5]

# for function to gather meta data from each HTML page 
for enter in hrefs: 
    for grant in enter[10:20]:
        driver.get(grant)
        time.sleep(3)
        #driver.maximize_window()
        html = driver.page_source
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    #scrapes contributions page and stores html in contributionspg
        contributions_button = driver.find_element_by_xpath('//a[contains(@id, "__BVID__9___BV_tab_button__")]')
        contributions_button.click()
        time.sleep(3)
        while True:
            loadingscroll(driver,7)
            break
        contributionspage = driver.page_source
    #scrapes activity page and stores html in activitypg
        activity_button = driver.find_element_by_xpath('//a[contains(@id, "__BVID__7___BV_tab_button__")]')
        activity_button.click()
        while True:
            scroll(driver, 6)
            break
        activitypage = driver.page_source
    #scrapes related grants page and stores html in rgpage
        # rg_button = driver.find_element_by_xpath('//a[contains(@id, "__BVID__11___BV_tab_button__")]')
        # rg_button.click()
        # time.sleep(3)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # while True:
        #     rgscroll(driver, 6)
        #     break
        # rgpage = driver.page_source

        date = datetime.datetime.now()
        capture1 = {"Grant Name": grant, "Home Page": html, "Activity": activitypage, "Contributions": contributionspage, "Date/Time": date}
        upload1 = collection2.insert_one(capture1)
        

#pymongo upload HTML pages to mongoDB
#add date-time 
    # capture1 = {"Grant Name": grant, "Home Page": html, "Activity": activitypage, "Contributions": contributionspage, "Date/Time": date}
    # upload1 = collection2.insert_one(capture1)

#pymongo upload HTML - Professor Weifeng's Code 
    # x = collection2.insert_one({"url": hrefs, "created_at": datetime.datetime.now()})
    # x1 = collection2.update_one({'_id': hrefs['_id']},
    #             {'$set': {'activity_html': activitypage, 'updated_at': datetime.datetime.now()}},
    #             upsert=False, multi=False)
    # x2 = collection2.update_one({'_id': hrefs['_id']},
    #             {'$set': {'contributions_html': contributionspage, 'updated_at': datetime.datetime.now()}},
    #             upsert=False, multi=False)
    # x3 = collection2.update_one({'_id': hrefs['_id']},
    #             {'$set': {'related_grants_html': rgpage, 'updated_at': datetime.datetime.now()}},
    #             upsert=False, multi=False)

driver.quit()










                         









   







    







# selenium imports
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
# other
import pickle
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
import os
import wget
import requests


# IG Crawler class which has seperated functions for crawling tools
class InstagramWebBot():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('detach', True)
    options.add_argument("--log-level=3")
    # options.add_argument('user-data-dir=selenium')
    s = Service('chromedriver.exe')
    driver = webdriver.Chrome(
        'chromedriver.exe',
        service=s,
        options=options,
    )
    wait = WebDriverWait(driver, 10)
    document_page = 'https://developers.google.com/'
    target_url = 'https://www.instagram.com/'

    # # call this func in order to save data in mongo db. You can pass both a dict or a nested list/dict
    def save_to_mongo(self, data, db_name, db_collection):
        cluster = MongoClient(
            'mongodb://localhost:27017/'
        )
        # in this case: 'naji'
        db = cluster[db_name]

        # in this case: 'instagram_crawler'
        collection = db[db_collection]
        post = data
        if type(data) == list:
            collection.insert_many(post)
        elif type(data) == dict:
            collection.insert_one(post)
        else:
            raise ValueError('mongodb has recieved a non-dict and non-list object.')
        collection.find_one()

    # class introducer once called
    def __str__(self):
        return f"Instagram web bot v1.0.0 " \
               f"By Selenium 4.3.0 " \
               f"Created by MesutFD " \
               f"Documentation page: {self.document_page} "

    # you may need to call this function before most of other functions in order to reach page first
    def go_to_page(self, target_url):
        self.driver.implicitly_wait(5)
        self.driver.get(
            target_url
        )

    # loging to IG. Pass username and password safely
    def login_to_instagram(self, username_, password_):
        self.go_to_page(self.target_url)
        try:
            accept_cookies = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "/ html / body / div[4] / div / div / button[2]")
            )).click()
            time.sleep(30)
        except:
            pass

        finally:
            username = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[name='username']")
            ))

            password = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[name='password']")
            ))
            username.clear()
            password.clear()

            username.send_keys(username_)
            password.send_keys(password_)

            log_in = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[type='submit']")
            )).click()

        not_now = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='react-root']/section/main/div/div/div/div/button")
        )).click()

        not_now2 = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Not Now')]")
        )).click()

        # todo: cookies not working. error message: cookies = pickle.load(open("src/app/cookies.pkl", "rb")) EOFError: Ran out of input
        cookies = pickle.load(open("src/app/cookies.pkl", "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        # self.driver.refresh()

    # get page followers data
    def get_page_followers(self, page='', page_url=''):
        if page != '':
            self.search_instagram(page)

        elif page_url != '':
            self.go_to_page(page_url)

        followers = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f"a[href='/{page}/followers/']")
        )).click()

        followers_box = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[2]")
        ))
        time.sleep(3)
        hover = ActionChains(webdriver).move_to_element(followers_box)
        hover.click_and_hold()
        while True:
            try:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_box)

            except:
                break

    # in case passing page url, don't forget to add / in the end of url address
    def get_page_general_info(self, page='', page_url='', scroll_times=0):
        if page != '':
            self.search_instagram(page)
            page_address = f"https://www.instagram.com/{page}/"

        elif page_url != '':
            self.go_to_page(page_url)
            page_address = page_url

        sectionElement = self.driver.find_element(By.XPATH,
                                                  "/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div/header/section")
        soup = BeautifulSoup(sectionElement.get_attribute('innerHTML'), "html.parser")
        numeric_elements = soup.findAll('span', {"class": "_ac2a"})
        PFF = [numeric.text for numeric in numeric_elements]
        followers_exact_count = numeric_elements[1]['title']

        if scroll_times > 0:
            for i in range(scroll_times):
                time.sleep(3)
                self.driver.execute_script("window.scrollTo(0, 4500);")
        time.sleep(2)
        divElement = self.driver.find_element(By.XPATH,
                                              "/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div/div[3]/article/div[1]/div")
        soup2 = BeautifulSoup(divElement.get_attribute('innerHTML'), "html.parser")
        posts_url = soup2.findAll('a', {
            "class": "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl _a6hd"})
        url_hrefs = [f"{page_address}{href['href'][1::]}" for href in posts_url]

        result = {}
        result['followers_count'] = followers_exact_count
        result['posts_count'] = PFF[0]
        result['following_count'] = PFF[2]
        result['last_12_post_url'] = url_hrefs

        return result

    # keyword to search. Supports both hashtag and non-hashtag
    def search_instagram(self, keyword=''):
        searchbox = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@placeholder='Search']")
        ))
        searchbox.clear()

        is_hashtag = []
        for i in keyword:
            is_hashtag.append(i)

        if is_hashtag[0] == '#':
            empty_str = ''
            hashtag_key = empty_str.join(map(str, is_hashtag[1:]))
            self.driver.get(f"{self.target_url}/explore/tags/{hashtag_key}")


        else:
            self.driver.get(f"{self.target_url}/{keyword}")

    # post information. Supports both page name and target url. Pass url with following format: target_url="http://url.co.uk/"
    def get_posts_info(self, page='', *args):
        if args['target_url']:
            self.go_to_page(args['target_url'])
        self.search_instagram(page)
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, 4000);")
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, 4000);")

    # extracting comments data. Uses ONLY target url. Returns a key-value json file
    def get_comments_by_post_url(self, post_url):
        # self.driver.get(post_url)
        self.go_to_page(post_url)
        while True:
            try:
                self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/li/div/button')
                )).click()
            except:
                break
        ulElement = self.driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/div[1]/ul')
        soup = BeautifulSoup(ulElement.get_attribute('innerHTML'), "html.parser")
        commends_elements = soup.findAll('span', {"class": "_aacl _aaco _aacu _aacx _aad7 _aade"})
        comment_user = soup.findAll('span', {"class": "_aap6 _aap7 _aap8"})
        print(len(commends_elements))
        print(len(comment_user))
        comment_result = [element.text for element in commends_elements]
        user_result = [element.text for element in comment_user]
        result = {}
        for i in range(len(commends_elements)):
            result[user_result[i]] = comment_result[i]

        return result

    time.sleep(4)


login = InstagramWebBot()
login.login_to_instagram(username_='zxcgfduyt', password_='123456789fdproo')

followers = login.search_instagram(keyword='#mesut')
print(followers)

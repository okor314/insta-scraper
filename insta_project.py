from dotenv import load_dotenv
import os
import time
import json
import datetime

from seleniumwire import webdriver
from seleniumwire.utils import decode as decodesw

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (StaleElementReferenceException, 
                                        TimeoutException)

from custom_waits import newPostAppeared

def errorCatcher(func, heandler, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        heandler(e)

class IstaScrap():
    def __init__(self, username):
        self.username = username
        self.userURL = f'https://www.instagram.com/{self.username}'

        chrome_options = Options()
        chrome_options.add_argument("--lang=en")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(options=chrome_options)

    def login(self):
        load_dotenv(override=True)
        self.browser.get('https://www.instagram.com')
        self.browser.maximize_window()

        user_input = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div[1]/div[1]/div/label/input')))
        #self.browser.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/div[1]/div/label/input')
        user_input.send_keys(f'{os.getenv('INSTA_NAME')}')

        pass_input = self.browser.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/div[2]/div/label/input')
        pass_input.send_keys(f'{os.getenv('INSTA_PASS')}')

        loggin_btn = self.browser.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/div[3]/button')
        loggin_btn.click()

        notnow_btn = WebDriverWait(self.browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@role, "button")]')))

        notnow_btn.click()
    
    def getPosts(self):
        reqs = driver.requests
        queries = [request for request in reqs if request.headers['x-root-field-name'] == 'xdt_api__v1__feed__user_timeline_graphql_connection']
        startPoint = len(queries) 

        self.browser.get(self.userURL)
        try:
            WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@role, "button")]')))
        except:
            pass

        fullData = []
        simpleData = {
            'type': [],
            'date': [],
            'description': [],
            'likes': [],
            'post_link': []
        }
        
        while True:   
            scrollHeight = self.browser.execute_script('return document.body.scrollHeight')

            visiblePosts = self.browser.find_elements(By.XPATH, '//a[contains(@href, "/p/") or contains(@href, "/reel/")]')

            newPosts = [post for post in visiblePosts if post.get_attribute('href') not in simpleData['post_link']]
            post_links = [post.get_attribute('href') for post in newPosts]
            post_types = [errorCatcher(lambda x: x.find_element(By.TAG_NAME, 'svg').get_attribute('aria-label'), lambda x: None, post) 
                    for post in newPosts]
            
            simpleData['type'].extend(post_types)
            simpleData['post_link'].extend(post_links)

            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')

            try:
                WebDriverWait(self.browser, 15, ignored_exceptions=StaleElementReferenceException)\
                    .until(newPostAppeared(simpleData['post_link']))
            except TimeoutException:
                newScrollHeight = self.browser.execute_script('return document.body.scrollHeight')
                if newScrollHeight == scrollHeight:
                    break
            
            reqs = self.browser.requests
            queries = [request for request in reqs if request.headers['x-root-field-name'] == 'xdt_api__v1__feed__user_timeline_graphql_connection']
            queries = queries[startPoint:]

            for querie in queries:
                response = querie.response

                data = decodesw(response.body, response.headers.get('Content-Encoding', 'identity'))
                jsonData = json.loads(data.decode('utf-8'))
                fullData.extend(jsonData['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges'])

            # Populate dictionary with simplified data
            simpleData['type'] = [post['node']['product_type'] for post in fullData]
            simpleData['date'] = [datetime.datetime.fromtimestamp(post['node']['taken_at'], datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
                                for post in fullData]
            
            simpleData['description'] = [post['node']['caption']['text'] for post in fullData]
            simpleData['likes'] = [post['node']['like_count'] for post in fullData]
            simpleData['post_link'] = [self.userURL + '/' + 
                                       post['node']['code'] for post in fullData]
            
            return simpleData, fullData

    def getProfileInfo(self):
        self.login()
        self.browser.get(self.userURL)
        try:
            WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@role, "button")]')))
        except:
            pass

        requests = self.browser.requests
        queries = [request for request in requests if request.headers['x-root-field-name'] == 'fetch__XDTUserDict']

        try:
            response = queries[0].response
            body = decodesw(response.body, response.headers.get('Content-Encoding', 'identity'))
            fullInfo = json.loads(body.decode('utf-8'))
        except:
            return
        
        userInfo = fullInfo['data']['user']
        profileInfo = {
            'username': userInfo['username'],
            'full_name': userInfo['full_name'],
            'biography': userInfo['biography'],
            'is_verified': userInfo['is_verified'],
            'follower_count': userInfo['follower_count'],
            'following_count': userInfo['following_count'],
            'post_count': userInfo['media_count'],
            'bio_links': userInfo['bio_links']
        }

        return profileInfo, fullInfo
    
    def getFollowers(self, stopAt):
        followersData = [{}]
        
        self.browser.get(self.userURL)
        followersButton = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "followers")]'))
        )

        req = self.browser.requests
        followersReq = [request for request in req if 'followers' in request.url]
        startPoint = len(followersReq)

        followersButton.click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@role, "dialog")]/div/div[2]/div/div/div[3]/div[1]/div/div[1]/div/div/div/div[3]/div/button'))
        )

        dialog = self.browser.find_element(By.XPATH, '//div[contains(@role, "dialog")]')

        while len(followersData) < stopAt:
            req = self.browser.requests
            followersReq = [request for request in req if 'followers' in request.url][-1]
            response = followersReq.response
            
            data = decodesw(response.body, response.headers.get('Content-Encoding', 'identity'))
            jsonData = json.loads(data.decode('utf-8'))
            if jsonData['users'][-1] == followersData[-1]:
                break
            followersData.extend(jsonData['users'])

            followers = dialog.find_elements(By.TAG_NAME, 'button')
            self.browser.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "smooth"});', followers[-1])
            time.sleep(1)
            
        followersData.pop(0)   
        
        return followersData
    
if __name__ == '__main__':
    user = 'zelenskyy_official'
    x =  IstaScrap(user)
    #x.login()
    info, _ = x.getProfileInfo()
    print(info)
from dotenv import load_dotenv
import os
import time

from selenium import webdriver
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
        self.browser = webdriver.Chrome(options=chrome_options)

    def login(self):
        # Checking if already login
        try:
            self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div')
        except:
            return

        load_dotenv(override=True)
        self.browser.get('https://www.instagram.com')
        self.browser.maximize_window()

        user_input = self.browser.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/div[1]/div/label/input')
        user_input.send_keys(f'{os.getenv('INSTA_NAME')}')

        pass_input = self.browser.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/div[2]/div/label/input')
        pass_input.send_keys(f'{os.getenv('INSTA_PASS')}')

        loggin_btn = self.browser.find_element(By.XPATH, '//*[@id="loginForm"]/div[1]/div[3]/button')
        loggin_btn.click()

        notnow_btn = WebDriverWait(self.browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@role, "button")]')))

        notnow_btn.click()
    
    def getPosts(self):
        self.browser.get(self.userURL)
        dataDict = {
            'type': [],
            'date': [],
            'description': [],
            'likes': [],
            'post_link': [],
            'content_link': []
        }
        
        while True:   
            scrollHeight = self.browser.execute_script('return document.body.scrollHeight')

            visiblePosts = self.browser.find_elements(By.XPATH, '//a[contains(@href, "/p/") or contains(@href, "/reel/")]')

            newPosts = [post for post in visiblePosts if post.get_attribute('href') not in dataDict['post_link']]
            post_links = [post.get_attribute('href') for post in newPosts]
            post_types = [errorCatcher(lambda x: x.find_element(By.TAG_NAME, 'svg').get_attribute('aria-label'), lambda x: None, post) 
                    for post in newPosts]
            
            dataDict['type'].extend(post_types)
            dataDict['post_link'].extend(post_links)

            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')

            try:
                WebDriverWait(self.browser, 15, ignored_exceptions=StaleElementReferenceException)\
                    .until(newPostAppeared(dataDict['post_link']))
            except TimeoutException:
                newScrollHeight = self.browser.execute_script('return document.body.scrollHeight')
                if newScrollHeight == scrollHeight:
                    break


if __name__ == '__main__':
    user = 'zelenskyy_official'
    x =  IstaScrap(user)
    x.login()
from dotenv import load_dotenv
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


class IstaScrap():
    def __init__(self, username):
        self.username = username
        self.browser = webdriver.Chrome()
        self.userURL = f'https://www.instagram.com/{self.username}'

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

        time.sleep(3)
        self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div/div/div').click()


if __name__ == '__main__':
    user = 'zelenskyy_official'
    x =  IstaScrap(user)
    x.login()
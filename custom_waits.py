class newPostAppeared():
    def __init__(self, checkedURLs):
        self.checkedURLs = checkedURLs

    def __call__(self, driver):
        try:
            visiblePosts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/") or contains(@href, "/reel/")]')
            post_links = [post.get_attribute('href') for post in visiblePosts]
            urlNotInCheckedList = [url not in self.checkedURLs for url in post_links]

            if any(urlNotInCheckedList):
                return True
            else:
                return False
        except:
            False

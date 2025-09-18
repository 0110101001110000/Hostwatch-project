
from selenium import webdriver
from src.utils.logger import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


# Init ---------------------------------------------------------------------- #


class Bot:
    def __init__(self):
        self.base_url = "https://www.booking.com/"
        self.driver   = self.setup()
        self.wait     = WebDriverWait(self.driver, timeout=10)
        self.actions  = ActionChains(self.driver)

    def setup(self):
        driver = webdriver.Chrome()
        driver.get(self.base_url)
        return driver

    def teardown(self):
        self.driver.quit()

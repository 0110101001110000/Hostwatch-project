
from time import sleep
from selenium import webdriver
from src.utils.logger import logger
from random import (randint, uniform)
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import MoveTargetOutOfBoundsException
from selenium.webdriver.common.action_chains import ActionChains


# Init ---------------------------------------------------------------------- #


class Selenium:
    def __init__(self):
        logger.name = "{}".format(self.get_name())

        logger.info("Inicializando {}...".format(self.__class__.__name__))

        self.driver  = self.setup()
        self.wait    = WebDriverWait(self.driver, timeout=10)
        self.actions = ActionChains(self.driver)

        logger.info("{} iniciado.".format(self.get_name()))

    def get(self, url):
        self.driver.get(url)

    def click(self, element):
        try:
            element_rect = element.rect

            start_x = element_rect["x"] + randint(1, (element_rect["width"] - 1))
            start_y = element_rect["y"] + randint(1, (element_rect["height"] - 1))

            self.actions.move_to_element_with_offset(element, start_x, start_y).perform()
        except MoveTargetOutOfBoundsException:
            self.actions.move_to_element(element).perform()
        finally:
            sleep(uniform(0.25, 1.5))

            self.actions.click(element).perform()

    def type(self, text_to_type):
        sleep(uniform(0.5, 2))

        for char in text_to_type:

            sleep(uniform(0.1, 0.5))

            self.actions.send_keys(char).perform()

    def scroll_down(self):
        amount_to_scroll = randint(300, 600)

        sleep(uniform(0.6, 2))

        self.driver.execute_script(f"window.scrollBy(0, {amount_to_scroll});")

    def scroll_up(self):
        amount_to_scroll = randint(300, 600)

        sleep(uniform(0.6, 2))

        self.driver.execute_script(f"window.scrollBy(0, -{amount_to_scroll});")

    def get_name(self):
        return self.__class__.__name__

    def setup(self):
        driver = webdriver.Chrome()
        return driver

    def teardown(self):
        self.driver.quit()

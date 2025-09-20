
from time import sleep
from selenium import webdriver
from src.utils.logger import logger
from selenium.webdriver.common.by import By
from random import (randint, uniform, random)
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import MoveTargetOutOfBoundsException
from selenium.webdriver.common.action_chains import ActionChains


# Init ---------------------------------------------------------------------- #


class BookingScrapper:
    def __init__(self):
        logger.info("Inicializando BookingScrapper...")

        self.base_url = "https://www.booking.com/"

        self.driver  = self.setup()
        self.wait    = WebDriverWait(self.driver, timeout=10)
        self.actions = ActionChains(self.driver)

        logger.info("BookingScrapper iniciado.")

    def select_language(self):
        logger.info("Selecionando linguagem...")

        element = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='header-language-picker-trigger']")
        self.wait.until(lambda _ : element.is_displayed())
        sleep(uniform(1, 2))
        self.click(element)

        element = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='selection-item'][lang='pt-br']")
        self.wait.until(lambda _ : element.is_displayed())
        sleep(uniform(1, 2))
        self.click(element)

        logger.info("Linguagem selecionada.")

    def select_coin(self, coin):
        logger.info("Selecionando moeda...")

        element = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='header-currency-picker-trigger']")
        self.wait.until(lambda _: element.is_displayed())
        sleep(uniform(1, 2))
        self.click(element)

        element  = None
        coin     = coin.lower()
        elements = self.driver.find_elements(By.CSS_SELECTOR, "button[data-testid='selection-item']")
        for el in elements:
            if coin in el.text.lower(): element = el
        assert element is not None, "A moeda %s não foi encontrada".format(coin.upper())
        self.wait.until(lambda _: element.is_displayed())
        sleep(uniform(1, 2))
        self.click(element)

        logger.info("Moeda selecionada.")

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
        amount_to_scroll = randint(100, 250)

        sleep(uniform(1, 2))

        self.driver.execute_script(f"window.scrollBy(0, {amount_to_scroll});")

    def scroll_up(self):
        amount_to_scroll = randint(150, 300)

        sleep(uniform(0.5, 2))

        self.driver.execute_script(f"window.scrollBy(0, -{amount_to_scroll});")

    def setup(self):
        driver = webdriver.Chrome()
        driver.get(self.base_url)
        return driver

    def teardown(self):
        self.driver.quit()

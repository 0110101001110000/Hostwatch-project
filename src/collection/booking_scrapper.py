
from time import sleep
from selenium import webdriver
from src.utils.logger import logger
from selenium.webdriver.common.by import By
from random import (randint, uniform, random)
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import MoveTargetOutOfBoundsException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


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

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='header-language-picker-trigger']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='selection-item'][lang='pt-br']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Linguagem selecionada.")

    def select_coin(self, coin):
        logger.info("Selecionando moeda...")

        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='header-currency-picker-trigger']")))
            sleep(uniform(0.5, 2))
            self.click(element)

            element = None
            coin    = coin.lower()

            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='selection-item']")))

            elements = self.driver.find_elements(By.CSS_SELECTOR, "button[data-testid='selection-item']")
            for el in elements:
                if coin in el.text.lower(): element = el

            assert element is not None, "A moeda %s não foi encontrada".format(coin.upper())

            sleep(uniform(0.5, 2))
            self.click(element)

            sleep(random())
            self.click(element)
        except StaleElementReferenceException:
            logger.info("Moeda selecionada.")


    def set_destination(self, destination):
        logger.info("Configurando destino...")

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='stays-search-box'] div[data-testid='destination-container']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        self.type(destination)

        logger.info("Destino configurado.")

    def set_dates(self, day, month, year, days_in="exact"):
        logger.info("Configurando data de check-in...")

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='stays-search-box'] button[data-testid='searchbox-dates-container'")))
        sleep(uniform(0.5, 2))
        self.click(element)

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"div[data-testid='searchbox-datepicker'] span[data-date='{year}-{month}-{day}']")))
        sleep(uniform(0.5, 2))
        #assert int(element.text) == int(day)
        self.click(element)

        days_in = days_in.lower()
        assert (days_in == "exact") or (days_in in ["1", "2", "3", "7"])
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"div[data-testid='datepicker-footer'] input[value='{days_in}']")))
        element = element.find_element(By.XPATH, "./..")
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Data de check-in configurada.")

    def set_occupancy(self):
        logger.info("Configurando ocupantes...")

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='stays-search-box'] button[data-testid='occupancy-config']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='occupancy-popup'] button")))
        element = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='occupancy-popup'] button")[-1]
        #assert element.text.lower().replace(" ", "") == "ok"
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Ocupantes configurados.")

    def search(self):
        logger.info("Pesquisando...")

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='stays-search-box'] button[type='submit']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Pesquisa realizada.")

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

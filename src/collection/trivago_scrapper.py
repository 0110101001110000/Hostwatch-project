
from time import sleep
from datetime import datetime
from src.utils.logger import logger
from src.utils.selenium import Selenium
from selenium.webdriver.common.by import By
from random import (randint, uniform, random)
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import StaleElementReferenceException, TimeoutException


# Init ---------------------------------------------------------------------- #


class TrivagoScrapper:
    def __init__(self, selenium_utils: Selenium):
        logger.name = "{}".format(self.get_name())

        logger.info("Inicializando {}...".format(self.get_name()))

        self.base_url       = "https://www.trivago.com.br/pt-BR/"
        self.selenium_utils = selenium_utils

        self.selenium_utils.get(self.base_url)

        logger.info("{} iniciado.".format(self.get_name()))

    def set_destination(self, destination):
        logger.info('Configurando destino para "{}"...'.format(destination))

        element = self.selenium_utils.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='input-auto-complete']")))
        sleep(uniform(0.5, 2))
        self.selenium_utils.click(element)

        self.selenium_utils.type(destination)

        logger.info("Destino configurado.")

    def set_dates(self, day, month, year):
        logger.info(
            'Configurando data de check-in para: "dia={0}", "mês={1}", "ano={2}"...'.format(
                day, month, year
            )
        )

        element = self.selenium_utils.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='search-form-calendar']")))
        sleep(uniform(0.5, 2))
        self.selenium_utils.click(element)

        now_month = int(datetime.now().month)
        assert (int(month) == now_month) or (int(month) == (now_month + 1)), "O mês deve ser o atual, ou o próximo, considerando a data da máquina local"
        element = self.selenium_utils.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='valid-calendar-day-{0}-{1}-{2}']".format(year, month, day))))
        sleep(uniform(0.5, 2))
        #assert int(element.text) == int(day)
        self.selenium_utils.click(element)

        logger.info("Data de check-in configurada.")

    def search(self):
        logger.info("Pesquisando...")

        element = self.selenium_utils.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='search-button-with-loader']")))
        sleep(uniform(0.5, 2))
        self.selenium_utils.click(element)

        logger.info("Pesquisa realizada.")

    def set_hotel_filter(self):
        logger.info("Filtrando tipo de propriedade para hotel...")

        element = self.selenium_utils.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='more_filters']")))
        sleep(random())
        self.selenium_utils.click(element)

        element = self.selenium_utils.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='popular-filters-category-checkbox-101/2']")))
        sleep(random())
        self.selenium_utils.click(element)

        element = self.selenium_utils.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='filters-popover-apply-button']")))
        sleep(uniform(3, 5))
        self.selenium_utils.click(element)

        logger.info("Tipo de propriedade filtrado para hotel.")

    def get_property_elements(self):
        logger.info("Obtendo elementos das propriedades...")

        while True:
            last_height = self.selenium_utils.driver.execute_script("return document.body.scrollHeight")

            if random() <= 0.20:
                self.selenium_utils.scroll_up()
                sleep(uniform(0.5, 2))

            self.selenium_utils.scroll_down()

            if random() <= 0.20: sleep(randint(1, 3))

            new_height = self.selenium_utils.driver.execute_script("return window.pageYOffset + window.innerHeight")
            total_height = self.selenium_utils.driver.execute_script("return document.body.scrollHeight")

            if new_height >= (total_height * 0.98):
                elements = self.selenium_utils.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "li[data-testid='accommodation-list-element']")))
                assert len(elements) > 0, "Nenhuma propriedade fora encontrada"
                logger.info("Elementos das propriedades obtidos.")
                return elements

    def get_property_information(self, elements: list):
        logger.info("Obtendo informações das propriedades...")

        properties_information = []
        for element in elements:
            try:
                title             = element.find_element(By.CSS_SELECTOR, "section[data-testid='item-name-section']").text
                recommended_units = element.find_element(By.CSS_SELECTOR, "div[data-testid='hotel-highlights-wrapper']").text
                review_score      = element.find_element(By.CSS_SELECTOR, "span[data-testid='aggregate-rating']").text
                final_price       = element.find_element(By.CSS_SELECTOR, "div[data-testid='recommended-price']").text

                properties_information.append({
                    "title"            : title,
                    "address"          : None,
                    "recommended_units": recommended_units,
                    "review_score"     : review_score,
                    "final_price"      : final_price
                })
            except:
                logger.warning(f"Erro ao obter informações do elemento: '''{element.text}'''")

        logger.info("Informações das propriedades obtidas.")

        return properties_information

    def get_name(self):
        return self.__class__.__name__

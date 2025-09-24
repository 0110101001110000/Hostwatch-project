
from time import sleep
from datetime import datetime
from selenium import webdriver
from src.utils.logger import logger
from selenium.webdriver.common.by import By
from random import (randint, uniform, random)
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import MoveTargetOutOfBoundsException, StaleElementReferenceException


# Init ---------------------------------------------------------------------- #


class BookingScrapper:
    def __init__(self):
        logger.info("Inicializando BookingScrapper...")

        self.base_url = "https://www.booking.com/"

        self.driver  = self.setup()
        self.wait    = WebDriverWait(self.driver, timeout=10)
        self.actions = ActionChains(self.driver)

        logger.info("BookingScrapper iniciado.")

    def select_idiom(self, idiom="pt-br"):
        logger.info('Selecionando o idioma "{}"...'.format(idiom))

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='header-language-picker-trigger']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='selection-item'][lang='{}']".format(idiom))))
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Idioma selecionado.")

    def select_coin(self, coin="brl"):
        logger.info('Selecionando a moeda "{}"...'.format(coin))

        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='header-currency-picker-trigger']")))
            sleep(uniform(0.5, 2))
            self.click(element)

            element = None
            mark    = (By.CSS_SELECTOR, "button[data-testid='selection-item']")
            coin    = coin.lower()

            self.wait.until(EC.element_to_be_clickable(mark))

            elements = self.driver.find_elements(*mark)
            for el in elements:
                if coin in el.text.lower(): element = el

            assert element is not None, 'A moeda "{}" não foi encontrada'.format(coin.upper())

            sleep(uniform(0.5, 2))
            self.click(element)

            sleep(random())
            self.click(element)
        except StaleElementReferenceException as error:
            logger.warning("Ocorreu um erro: {}".format(error.msg))

        logger.info("Moeda selecionada.")

    def set_destination(self, destination):
        logger.info('Configurando destino para "{}"...'.format(destination))

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='searchbox-layout-wide'] div[data-testid='destination-container']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        self.type(destination)

        logger.info("Destino configurado.")

    def set_dates(self, day, month, year, days_in="exact"):
        logger.info(
            'Configurando data de check-in para: "dia={0}", "mês={1}", "ano={2}", "quantidade_de_dias={3}"...'.format(
                day, month, year, days_in
            )
        )

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='searchbox-layout-wide'] button[data-testid='searchbox-dates-container'")))
        sleep(uniform(0.5, 2))
        self.click(element)

        now_month = int(datetime.now().month)
        assert (int(month) == now_month) or (int(month) == (now_month + 1)), "O mês deve ser o atual, ou o próximo, considerando a data da máquina local"
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='searchbox-datepicker'] span[data-date='{0}-{1}-{2}']".format(year, month, day))))
        sleep(uniform(0.5, 2))
        #assert int(element.text) == int(day)
        self.click(element)

        days_in = days_in.lower()
        assert (days_in == "exact") or (days_in in ["1", "2", "3", "7"]), 'A quantidade de dias somente pode ser: "1", "2", "3", "7" ou "exact"'
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"div[data-testid='datepicker-footer'] input[value='{days_in}']")))
        element = element.find_element(By.XPATH, "./..")
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Data de check-in configurada.")

    def set_occupancy(self):
        logger.info("Configurando ocupantes...")

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='searchbox-layout-wide'] button[data-testid='occupancy-config']")))
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

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='searchbox-layout-wide'] button[type='submit']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Pesquisa realizada.")

    def set_hotel_filter(self):
        logger.info("Filtrando tipo de propriedade para hotel...")

        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='filters-group-container'] div[data-filters-item='ht_id:ht_id=204']")))
        sleep(uniform(0.5, 2))
        self.click(element)

        logger.info("Tipo de propriedade filtrado para hotel.")

    def get_property_elements(self):
        logger.info("Obtendo elementos das propriedades...")

        while True:
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            if random() <= 0.20:
                self.scroll_up()
                sleep(uniform(0.5, 2))

            self.scroll_down()

            if random() <= 0.20: sleep(randint(1, 3))

            new_height = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
            total_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height >= (total_height * 0.98):
                elements = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='property-card-container']")))
                assert len(elements) > 0, "Nenhuma propriedade fora encontrada"
                logger.info("Elementos das propriedades obtidos.")
                return elements

    def get_property_information(self, elements: list):
        logger.info("Obtendo informações das propriedades...")

        properties_information = []
        for element in elements:
            try:
                title             = element.find_element(By.CSS_SELECTOR, "div[data-testid='title']").text
                address           = element.find_element(By.CSS_SELECTOR, "span[data-testid='address']").text
                recommended_units = element.find_element(By.CSS_SELECTOR, "div[data-testid='recommended-units']").text
                review_score      = element.find_element(By.CSS_SELECTOR, "div[data-testid='review-score']").text
                final_price       = element.find_element(By.CSS_SELECTOR, "span[data-testid='price-and-discounted-price']").text

                properties_information.append({
                    "title"            : title,
                    "address"          : address,
                    "recommended_units": recommended_units,
                    "review_score"     : review_score,
                    "final_price"      : final_price
                })
            except:
                logger.warning(f"Erro ao obter informações do elemento: '''{element.text}'''")

        logger.info("Informações das propriedades obtidas.")

        return properties_information

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

    def setup(self):
        driver = webdriver.Chrome()
        driver.get(self.base_url)
        return driver

    def teardown(self):
        self.driver.quit()

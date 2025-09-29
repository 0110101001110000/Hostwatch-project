
import os
import pandas as pd
from datetime import datetime
from random import (sample, random)
from src.utils.logger import logger
from src.utils.selenium import Selenium
from src.collection.booking_scrapper import BookingScrapper
from src.collection.trivago_scrapper import TrivagoScrapper


# Functions ----------------------------------------------------------------- #


def random_order(*actions):
    for func, *args in sample(actions, len(actions)):
        func(*args)

def start_booking_scrapper_scrapping(
        location,
        day,
        month,
        year,
        days_in,
        language,
        coin,
        output_dir,
        accept_cookie_prob=0.5,
        save_csv=True
):
    logger.info("Iniciando scrapping...")

    start_time           = datetime.now()
    formatted_start_time = start_time.strftime("%d-%m-%Y %H:%M:%S")

    if random() <= accept_cookie_prob: booking_bot.decline_cookie()
    else: booking_bot.accept_cookie()

    random_order(
        (booking_bot.select_idiom, language),
        (booking_bot.select_coin, coin)
    )
    random_order(
        (booking_bot.set_destination, location),
        (booking_bot.set_dates, day, month, year, days_in),
        (booking_bot.set_occupancy,)
    )
    booking_bot.search()
    booking_bot.set_hotel_filter()

    property_elements    = booking_bot.get_property_elements()
    property_information = booking_bot.get_property_information(property_elements)

    if save_csv:
        df = pd.DataFrame(property_information)

        os.makedirs(output_dir, exist_ok=True)
        SCRAPPING_FILE = os.path.join(output_dir, f"Booking {location} {formatted_start_time}.csv")
        df.to_csv(SCRAPPING_FILE, index=False)

    logger.info("Scrapping finalizado.")

def start_trivago_scrapper_scrapping(
        location,
        day,
        month,
        year,
        output_dir,
        save_csv=True
):
    logger.info("Iniciando scrapping...")

    start_time           = datetime.now()
    formatted_start_time = start_time.strftime("%d-%m-%Y %H:%M:%S")

    random_order(
        (trivago_bot.set_destination, location),
        (trivago_bot.set_dates, day, month, year)
    )
    trivago_bot.search()
    trivago_bot.set_hotel_filter()

    property_elements    = trivago_bot.get_property_elements()
    property_information = trivago_bot.get_property_information(property_elements)

    if save_csv:
        df = pd.DataFrame(property_information)

        os.makedirs(output_dir, exist_ok=True)
        SCRAPPING_FILE = os.path.join(output_dir, f"Trivago {location} {formatted_start_time}.csv")
        df.to_csv(SCRAPPING_FILE, index=False)

    logger.info("Scrapping finalizado.")


# Init ---------------------------------------------------------------------- #


if __name__ == "__main__":
    logger.name = "scrapping.py"

    selenium_utils = Selenium()

    language      = "pt-br"
    coin          = "brl"
    location      = "Tiradentes Minas Gerais"
    day           = "01"
    month         = "10"
    year          = "2025"
    days_in       = "1"
    SCRAPPING_DIR = "../../data/raw"

    booking_bot = BookingScrapper(selenium_utils)
    #start_booking_scrapper_scrapping(location, day, month, year, days_in, language, coin, SCRAPPING_DIR)

    trivago_bot = TrivagoScrapper(selenium_utils)
    start_trivago_scrapper_scrapping(location, day, month, year, SCRAPPING_DIR)

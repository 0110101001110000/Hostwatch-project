
import os
import pandas as pd
from datetime import datetime
from random import (sample, random)
from src.utils.logger import logger
from src.collection.booking_scrapper import BookingScrapper
from src.utils.selenium import Selenium


# Functions ----------------------------------------------------------------- #


def random_order(*actions):
    for func, *args in sample(actions, len(actions)):
        func(*args)


# Init ---------------------------------------------------------------------- #


if __name__ == "__main__":
    logger.name = "scrapping.py"

    logger.info("Iniciando scrapping...")

    start_time           = datetime.now()
    formatted_start_time = start_time.strftime("%d-%m-%Y %H:%M:%S")

    selenium_utils = Selenium()
    booking_bot    = BookingScrapper(selenium_utils)

    language      = "pt-br"
    coin          = "brl"
    location      = "Florianópolis"
    day           = "01"
    month         = "10"
    year          = "2025"
    days_in       = "1"
    SCRAPPING_DIR = "../../data/interim"

    if random() <= 0.5: booking_bot.decline_cookie()
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

    df = pd.DataFrame(property_information)

    os.makedirs(SCRAPPING_DIR, exist_ok=True)
    SCRAPPING_FILE = os.path.join(SCRAPPING_DIR, f"{location} {formatted_start_time}.csv")
    df.to_csv(SCRAPPING_FILE, index=False)

    logger.info("Scrapping finalizado.")


import os
import pandas as pd
from random import sample
from datetime import datetime
from src.collection.booking_scrapper import BookingScrapper


# Functions ----------------------------------------------------------------- #


def random_order(*actions):
    for func, *args in sample(actions, len(actions)):
        func(*args)


# Init ---------------------------------------------------------------------- #


if __name__ == "__main__":
    start_time           = datetime.now()
    formatted_start_time = start_time.strftime("%d-%m-%Y %H:%M:%S")

    booking_bot = BookingScrapper()

    language = "en-us"
    coin     = "usd"
    location = "Kyoto Japan"
    day      = "06"
    month    = "10"
    year     = "2025"
    days_in  = "1"

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

    SCRAPPING_DIR = "../../data/interim"
    os.makedirs(SCRAPPING_DIR, exist_ok=True)
    SCRAPPING_FILE = os.path.join(SCRAPPING_DIR, f"{location} {formatted_start_time}.csv")
    df.to_csv(SCRAPPING_FILE, index=False)

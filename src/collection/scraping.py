
import os
import datetime
import pandas as pd
from random import sample
from src.collection.booking_scrapper import BookingScrapper


# Functions ----------------------------------------------------------------- #


def random_order(*actions):
    for func, *args in sample(actions, len(actions)):
        func(*args)


# Init ---------------------------------------------------------------------- #


if __name__ == "__main__":
    start_time = datetime.datetime.now()

    booking_bot = BookingScrapper()

    language = "en-us"
    coin     = "usd"
    location = "Kyoto Japan"

    random_order(
        (booking_bot.select_language, language),
        (booking_bot.select_coin, coin)
    )
    random_order(
        (booking_bot.set_destination, location),
        (booking_bot.set_dates, "01", "01", "2026", "7"),
        (booking_bot.set_occupancy,)
    )
    booking_bot.search()
    booking_bot.set_hotel_filter()

    property_elements    = booking_bot.get_property_elements()
    property_information = booking_bot.get_property_information(property_elements)

    df = pd.DataFrame(property_information)

    SCRAPPING_DIR = "../../data/interim"
    os.makedirs(SCRAPPING_DIR, exist_ok=True)
    SCRAPPING_FILE = os.path.join(SCRAPPING_DIR, f"{location} {start_time}.csv")
    df.to_csv(SCRAPPING_FILE, index=False)

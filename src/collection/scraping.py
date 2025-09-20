
from src.collection.booking_scrapper import BookingScrapper


# Init ---------------------------------------------------------------------- #


if __name__ == "__main__":
    booking_bot = BookingScrapper()

    booking_bot.select_language()
    booking_bot.select_coin("brl")

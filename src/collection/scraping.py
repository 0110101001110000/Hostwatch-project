
from src.collection.booking_scrapper import BookingScrapper


# Init ---------------------------------------------------------------------- #


if __name__ == "__main__":
    booking_bot = BookingScrapper()

    booking_bot.select_language()
    booking_bot.select_coin("brl")
    booking_bot.set_destination("São Paulo Brasil")
    booking_bot.set_dates("01", "10", "2025", "1")
    booking_bot.set_occupancy()
    booking_bot.search()

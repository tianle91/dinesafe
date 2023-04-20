from datetime import date

YMD_FORMAT = "%Y-%m-%d"

assert date(2022, 4, 29).strftime(YMD_FORMAT) == "2022-04-29"

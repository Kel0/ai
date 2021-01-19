import csv
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
from transliterate import translit

from database.models import Alias
from settings import ABS_PATH, WIKI_BASE_URL, WIKI_CITY_POSTFIX


def get_cities() -> List[str]:
    """
    Read cities.txt file and return its' value as list
    :return: List of cities
    """
    with open(os.path.join(ABS_PATH, "Resources/cities.txt"), "r") as f:
        return json.loads(f.read())


def get_world_cities():
    cities = []
    with open(os.path.join(ABS_PATH, "Resources/worldcities.csv"), "r") as f:
        reader = csv.reader(f)

        for index, val in enumerate(reader):
            if index == 0:
                continue
            cities.append(val[1])

    return set(cities)


class Wiki:
    def __init__(self):
        self.base_url = WIKI_BASE_URL + WIKI_CITY_POSTFIX

    def get_html(self, url: Optional[str] = None) -> bytes:
        if url is None:
            url = self.base_url

        response = requests.get(url)
        return response.content

    def scrape_cities(self):
        cities = []
        html = self.get_html()
        soup = bs(html, "lxml")

        def get_links(_soup):
            links = []
            mw_category = _soup.find("div", attrs={"class": "mw-category"})
            category_groups = mw_category.find_all(
                "div", attrs={"class": "mw-category-group"}
            )

            for category_group in category_groups:
                lis = category_group.find("ul").find_all("li")

                for li in lis:
                    links.append(li.find("a").get("href"))

            return links

        def get_cities(_soup):  # noqa
            pass

        cities_links = get_links(_soup=soup)

        for city_link in cities_links:
            html = self.get_html(url=WIKI_BASE_URL + city_link)
            soup = bs(html, "lxml")
            wikitable = (
                soup.find("table", attrs={"class": "wikitable"})
                .find("tbody")
                .find_all("tr")
            )

            for tr in wikitable[1:]:
                tds = tr.find_all("td")

                if len(tds) > 0:
                    cities.append(tds[1].text)

            print(cities)


class WeatherProcessor:
    def __init__(self, text: str) -> None:
        self.text = text
        self.intent = False
        self._check()

    def _check(self) -> None:
        """
        Check sentence for intent.
        """
        if "погода" in self.text:
            self.intent = True

    def get_date(self) -> datetime.date:
        """
        Parse date from string
        :return: datetime.date object
        """
        date_aliases = Alias.get(origin="date").matches
        split_text = self.text.split()

        for date_alias in date_aliases:

            if isinstance(date_alias, str):
                if date_alias not in self.text:
                    continue
                return date_alias

            subs = []
            for sub_date_key in date_alias:
                if sub_date_key in self.text:
                    subs.append(True)

            if all(subs):
                try:
                    first_element_index = self.text.split().index(date_alias[0])
                    last_element_index = self.text.split().index(date_alias[-1])
                except ValueError:
                    continue

                if date_alias[0].lower() == "через":
                    first_element_index = first_element_index + 1
                    days = int(split_text[first_element_index:last_element_index][0])
                    return (datetime.now() + timedelta(days=days)).date()

                elif date_alias[-1].lower() == "назад":
                    first_element_index = first_element_index - 1

                    try:
                        days = int(
                            split_text[first_element_index : last_element_index - 1][0]
                        )
                    except ValueError:
                        days = int(
                            split_text[first_element_index + 2 : last_element_index][0]
                        )

                    return (datetime.now() - timedelta(days=days)).date()

        return datetime.now().date()

    def get_city(self) -> Optional[str]:
        """
        Parse city from string
        :return: City name string
        """
        cities = get_world_cities()
        translit_text = translit(self.text, reversed=True)
        match = process.extractBests(translit_text, cities)

        if match[1] == 0 or match[1] < 70:
            return None

        return match[0]


p = WeatherProcessor("погода в Алмате на завтра")
print(p.get_city())

import asyncio
import os
import re

import aiohttp
import click
import requests
from bs4 import BeautifulSoup

from utils import parse_working_hours
from utils import write_data_to_csv
from utils import write_data_to_json


class Parser:
    def __init__(self, link):
        self.url = link
        self.all_links = []
        self.data = []

    def get_all_links(self):
        """Getting all shop links on the site"""
        response = requests.get(url=self.url)
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.find_all("ul", class_="sub-menu")
        for item in items:
            self.all_links.extend(
                ["https://oriencoop.cl" + i["href"] for i in item.find_all("a")]
            )

    async def parse_data(self, link):
        """Getting all needed data from provided link"""
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                soup = BeautifulSoup(await resp.text(), "lxml")
                all_items = soup.find_all("div", class_="sucursal")
                for item in all_items:
                    address = item.find("div", class_="s-dato").find("span").text
                    coord = item.find("div", class_="s-mapa").find("iframe")["src"]
                    lat = " ".join(re.findall(r"2d([^<>]+)!", coord)).split("!")[0]
                    lon = " ".join(re.findall(r"3d([^<>]+)!", coord)).split("!")[0]
                    latlon = [float(lat), float(lon)]
                    name = "Oriencoop"
                    first_phone = item.select(
                        ".s-dato > p:nth-child(3) > span:nth-child(3)"
                    )[0].text.replace("-", "")
                    second_phone = soup.select(".b-call > a:nth-child(3)")[0].text
                    third_phone = soup.select(".b-call > a:nth-child(6)")[
                        0
                    ].text.replace(" ", "")
                    phones = [first_phone, second_phone, third_phone]
                    morning = item.select(
                        ".s-dato > p:nth-child(5) > span:nth-child(3)"
                    )[0].text
                    afternoon = item.select(
                        ".s-dato > p:nth-child(5) > span:nth-child(5)"
                    )[0].text
                    working_hours = parse_working_hours(morning, afternoon)
                    result = {
                        "address": address,
                        "latlon": latlon,
                        "name": name,
                        "phones": phones,
                        "working_hours": working_hours,
                    }
                    self.data.append(result)

    def runner(self):
        print(f"Start parsing data from {self.url}")
        self.get_all_links()
        tasks = [self.parse_data(link) for link in self.all_links]
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(asyncio.wait(tasks))
        return self.data


@click.command()
@click.option(
    "-o",
    "--output",
    default="json",
    type=click.Choice(["json", "csv"]),
    help=f"Choose processing type",
    show_default=True,
)
def main(output: str):
    url = "https://oriencoop.cl/sucursales.htm"
    parser = Parser(url)
    data = parser.runner()
    if output == "csv":
        write_data_to_csv(data, "task1.csv")
    else:
        write_data_to_json(data, "task1.json")


if __name__ == "__main__":
    main()

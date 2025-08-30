import json
import urllib.robotparser
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

import requests
from recipe_scrapers import scrape_html

from .scraped_recipe import ScrapedRecipe

NYT_COOKING_BASE_URL = "https://cooking.nytimes.com"
NYT_COOKING_ROBOTS_URL = f"{NYT_COOKING_BASE_URL}/robots.txt"
DEFAULT_CRAWL_DELAY_SECONDS = 5


class Downloader:
    def __init__(
        self, robots_parser: Optional[urllib.robotparser.RobotFileParser] = None
    ) -> None:
        self.robots_parser = robots_parser or self.__robots_file_parser(
            NYT_COOKING_ROBOTS_URL
        )

    def download(self, source: str) -> ScrapedRecipe:
        recipe_json = None

        if source.startswith("http") and source.startswith(NYT_COOKING_BASE_URL):
            recipe_json = self.__download_nyt_recipe(source)
        elif source.startswith("http"):
            recipe_json = self.__download_arbitrary_recipe(source)
        else:
            path = f"{Path(__file__).parent.parent}{source}"
            with open(path) as fh:
                recipe_json = json.load(fh)

        return ScrapedRecipe(recipe_json)

    # TODO: Update this method to take a URL and produce the right delay for
    # that URL in particular.
    @cached_property
    def delay(self) -> int:
        requested_crawl_delay = self.robots_parser.crawl_delay("*")
        return requested_crawl_delay or DEFAULT_CRAWL_DELAY_SECONDS

    def __download_nyt_recipe(self, url: str) -> dict[Any, Any]:
        if not self.robots_parser.can_fetch("*", url):
            raise

        return scrape_html(requests.get(url).text, org_url=url).to_json()  # type: ignore

    def __download_arbitrary_recipe(self, url: str) -> dict[Any, Any]:
        return scrape_html(
            requests.get(url).text, org_url=url, wild_mode=True
        ).to_json()  # type: ignore

    def __robots_file_parser(self, root_url: str) -> urllib.robotparser.RobotFileParser:
        robots = urllib.robotparser.RobotFileParser(root_url)
        robots.read()
        return robots

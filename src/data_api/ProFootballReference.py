"""
Script to fetch NFL player names from pro-football-reference.com
and store them in a list.
"""

from bs4 import BeautifulSoup as soup

import pandas as pd
import requests
import time

from src.utils import FuzzyNameSearcher, PFRScraper
from src.data_api.data_dicts import PFR_DATA_DICT  


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text

def extract_names(html, names):
    page_soup = soup(html, 'html.parser')
    div_players = page_soup.find('div', {'id': 'div_players'})
    if not div_players:
        return names

    player_links = div_players.find_all('a', href=True)
    for link in player_links:
        name = link.text.strip()
        # check that name nonempty
        if not name:
            continue

        # Check if link contains a <b> or <strong> child (i.e. bold)
        # or if link’s parent is bold, etc.
        bold_child = link.find(['b', 'strong'])
        parent_bold = link.parent and link.parent.name in ('b', 'strong')

        if bold_child or parent_bold:
            if name not in names:
                names.append(name)
    return names

def extract_links(html, links):
    page_soup = soup(html, 'html.parser')
    div_players = page_soup.find('div', {'id': 'div_players'})
    if not div_players:
        return links

    player_links = div_players.find_all('a', href=True)
    for link in player_links:
        href = link['href']
        # Check if link contains a <b> or <strong> child (i.e. bold)
        # or if link’s parent is bold, etc.
        bold_child = link.find(['b', 'strong'])
        parent_bold = link.parent and link.parent.name in ('b', 'strong')

        if (bold_child or parent_bold):
            if href not in links:
                links.append(href)
    return links

class PFR: # Pro-Football Reference
    def __init__(self):
        alphabet_capitalized = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.base_url = 'https://www.pro-football-reference.com/'
        self.player_url = self.base_url + "players/"
        self.table_names = ["rushing_and_receiving", "kicking", "passing", "defense"]
        self.names = []
        self.links = []
        for letter in alphabet_capitalized:
            url = self.base_url + letter + '/'
            html = get_html(url)
            extract_names(html, self.names)
            extract_links(html, self.links)

        # Utility Objects
        self.fuzzy = FuzzyNameSearcher(names)
        self.scraper = PFRScraper(self.base_url, self.table_names)

        # Allow links to be searchable by name
        self.player_dict = {name: link for name, link in zip(self.names, self.links)}  

    def _search_link_from_name(self, name: str) -> str | None:
        player = self.fuzzy.best_match(name)
        if player is None:
            print("No valid match found")
            return None
        return self.player_dict.get(player, None) # Return the link
    
    def get_player_stats(self, name: str, year: str | int) -> pd.DataFrame:
        player_link = self._search_link_from_name(name)

        player_stats = self.scraper._get_player_stats_table(player_link)

        return pd.DataFrame(player_stats)

if __name__ == "__main__":
    alphabet_capitalized = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    base_url = 'https://www.pro-football-reference.com/players/'
    names = []

    for letter in alphabet_capitalized:
        url = f"{base_url}{letter}/"
        print(f"Fetching links from: {url}")
        print("Getting letter: ", letter)
        html = get_html(url)
        extract_names(html, names)
        time.sleep(4)  # Be polite and avoid hammering the server

    with open('nfl_players.txt', 'w') as f:
        for name in sorted(names):
            f.write(name + '\n')

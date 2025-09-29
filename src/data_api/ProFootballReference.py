"""
Script to fetch NFL player names from pro-football-reference.com
and store them in a list.
"""
from bs4 import BeautifulSoup as soup

import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

from utils import FuzzyNameSearcher, PFRScraper, normalize
from .data_dicts import PFR_DATA_DICT  

load_dotenv()

def get_html(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text

class PFR: # Pro-Football Reference
    def __init__(self):
        alphabet_capitalized = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.base_url = 'https://www.pro-football-reference.com'
        self.table_names = ["rushing_and_receiving", "kicking", "passing", "defense"]
        self.scraper = PFRScraper(self.base_url, self.table_names)

        self.names = []
        self.links = []

        names_path = os.getenv("PLAYER_NAMES_PATH")
        links_path = os.getenv("PLAYER_LINKS_PATH")

        # Get names and links if stored
        if names_path:
            with open(names_path, "r") as f:
                self.names = [line.strip() for line in f.readlines()]

        if links_path:
            with open(links_path, "r") as f:
                self.links = [line.strip() for line in f.readlines()]

        if not self.names or not self.links:
            # Populate the names and links
            for letter in alphabet_capitalized:
                url = self.player_url + "players/" + letter + '/'
                html = get_html(url)
                self.scraper.extract_names(html, self.names)
                self.scraper.extract_links(html, self.links)

        # Utility Objects
        self.fuzzy = FuzzyNameSearcher(self.names)

        # Allow links to be searchable by name
        self.player_dict = {name: link for name, link in zip(self.names, self.links)}  

    def _search_link_from_name(self, name: str) -> str | None:
        player, score = self.fuzzy.best_match(name)
        if player is None:
            print("No valid match found")
            return None
        print(self.player_dict.get(player, None)) # Return the link
        return self.player_dict.get(player, None) # Return the link
    
    def get_player_stats(self, name: str, year: str | int = None) -> pd.DataFrame:
        """
            Returns a dataframe of a player's seasonal stats by a requested season if passed.
            Tries to match the best name to the query name using fuzzy matching.
            WARNING:
                IF BEING USED DURING ITERATION, ENFORCE RATE LIMITING TO AVOID BEING BLOCKED BY PFR'S SERVER.
                IT IS RECOMMENDED TO WAIT 5 SECONDS BETWEEN QUERIES.
        """
        player_link = self._search_link_from_name(name)

        if not player_link:
            print("No matching player was found")
            return 
                
        player_stats = self.scraper.scrape_player_stats(self.base_url + player_link)

        if year is not None:
            if str(year) in player_stats.keys():
                player_stats_temp = {}
                player_stats_temp[str(year)] = player_stats[str(year)]
                player_stats = player_stats_temp
                del player_stats_temp

        stats_df = pd.DataFrame(player_stats)

        # Final Normalization
        # Make the year_id = column_id for each column
        for year in stats_df:
            stats_df["query_name"] = name # Save the query name for matching later
            stats_df.loc["year_id", year] = year

        return stats_df.T # Transpose the columns and rows

if __name__ == "__main__":
    alphabet_capitalized = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    base_url = 'https://www.pro-football-reference.com/players/'
    names = []

    scraper = PFRScraper()
    for letter in alphabet_capitalized:
        url = f"{base_url}{letter}/"
        print(f"Fetching links from: {url}")
        print("Getting letter: ", letter)
        html = get_html(url)
        scraper.extract_names(html, names)
        time.sleep(4)  # Be polite and avoid hammering the server

    with open('nfl_players.txt', 'w') as f:
        for name in sorted(names):
            f.write(name + '\n')

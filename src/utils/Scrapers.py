from __future__ import annotations
from typing import Dict, Tuple, Iterable
import requests
from bs4 import BeautifulSoup

class PFRScraper:
    def __init__(self, base_url: str, table_names: list[str]):
        self.base_url = base_url.rstrip("/")
        self.table_names = table_names

    # --- Public API ---------------------------------------------------------
    
    def extract_names(html, names: list[str | None]) -> list[str]:
        page_soup = BeautifulSoup(html, 'html.parser')
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

    def extract_links(html, links: list[str | None]) -> list[str]:
        page_soup = BeautifulSoup(html, 'html.parser')
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
    
    def scrape_player_stats(self, link: str) -> Dict[str, Dict[str, str]]:
        """Fetch page, locate the first relevant table, and parse season rows."""
        html = self._get_html(link)
        soup = self._soup_from_html(html)
        table, table_id = self._get_player_stats_table(soup)
        header_fields = self._pick_header_fields(table, table_id)
        return self._parse_body_rows(table, header_fields)

    # --- HTTP / HTML helpers -----------------------------------------------

    def _get_html(self, url: str) -> str:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.text

    def _soup_from_html(self, html: str) -> BeautifulSoup:
        # Sports-Reference often hides tables in HTML comments; un-comment if needed. 
        # (Simplest approach shown here; alternative is parsing Comment nodes directly.)
        # refs: SO threads on comment-wrapped tables
        if "<!--" in html and "-->" in html:
            html = html.replace("<!--", "").replace("-->", "")
        return BeautifulSoup(html, "html.parser")

    # --- Table discovery ----------------------------------------------------

    def _get_player_stats_table(self, page_soup: BeautifulSoup) -> Tuple[BeautifulSoup, str]:
        """Return the first <table> whose id is in self.table_names."""
        # Fast path with CSS selector in document order
        selector = ",".join(f"table#{tid}" for tid in self.table_names)
        table = page_soup.select_one(selector)
        if not table:
            raise ValueError("No matching stats table found on page.")
        table_id = table.get("id", "")
        return table, table_id

    # --- Header handling ----------------------------------------------------

    def _pick_header_fields(self, table: BeautifulSoup, table_id: str) -> list[str]:
        """Choose which header row to use and return normalized field names."""
        rows = table.find_all("tr")
        if not rows:
            raise ValueError("Stats table has no rows.")
        header_row = rows[0] if table_id == "passing" else (rows[1] if len(rows) > 1 else rows[0])
        ths = header_row.find_all(["th", "td"])
        # Use data-stat when available; fallback to text
        fields = [th.get("data-stat") or th.get_text(strip=True) for th in ths]
        return fields

    # --- Body parsing -------------------------------------------------------

    def _parse_body_rows(self, table: BeautifulSoup, fields: list[str]) -> Dict[str, Dict[str, str]]:
        """Parse <tbody> rows into {season: {field: value}}."""
        tbody = table.find("tbody") or table
        out: Dict[str, Dict[str, str]] = {}
        for tr in self._iter_season_rows(tbody):
            season_key, row_data = self._parse_row(tr, fields)
            if season_key:
                out[season_key] = row_data
        return out

    def _iter_season_rows(self, tbody: BeautifulSoup) -> Iterable[BeautifulSoup]:
        # Skip header/subtotal rows that sometimes appear in TBODY
        for tr in tbody.find_all("tr"):
            if tr.get("class") and "thead" in tr.get("class", []):
                continue
            yield tr

    def _parse_row(self, tr: BeautifulSoup, fields: list[str]) -> Tuple[str | None, Dict[str, str]]:
        # Season is usually the row header (<th>)
        th = tr.find("th")
        season = th.get_text(strip=True) if th else None
        # map td[data-stat] -> text
        cells = tr.find_all("td")
        row: Dict[str, str] = {}
        for td in cells:
            key = td.get("data-stat")
            if not key:
                continue
            row[key] = td.get_text(strip=True)
        # Optional: align with header fields (keep only known fields)
        if fields:
            row = {k: row.get(k, "") for k in fields if k}  # stable order
        return season, row
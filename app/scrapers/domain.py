import time
from typing import List
from urllib.parse import urljoin
from scrapling.fetchers import StealthySession
from app.models.property import PropertyListing
from app.scrapers.base import BasePropertyScraper
from app.utils.logger import logger


class DomainScraper(BasePropertyScraper):
    source_name: str = "domain"

    def scrape_suburb(
        self, suburb: str, state: str, postcode: str, max_pages: int = 1
    ) -> List[PropertyListing]:
        listings: List[PropertyListing] = []
        suburb_slug = f"{suburb.lower().replace(' ', '-')}-{state.lower()}-{postcode}"
        base_url = f"https://www.domain.com.au/sale/{suburb_slug}/"

        logger.info(f"[{self.source_name}] Starting suburb scrape for {suburb_slug}")

        with StealthySession(headless=self.headless, real_chrome=True) as session:
            for page_num in range(1, max_pages + 1):
                url = f"{base_url}?page={page_num}"
                logger.info(f"[{self.source_name}] Fetching page {page_num}: {url}")

                try:
                    page = session.fetch(
                        url,
                        wait_selector="[data-testid='results']",
                        wait=3000,
                        network_idle=True,
                    )

                    if page.status != 200:
                        logger.error(f"[{self.source_name}] Page {page_num} returned HTTP {page.status}")
                        break

                    cards = page.css('[data-testid="data-observer-listing-card"]')
                    if not cards:
                        cards = page.css('ul[data-testid="results"] > li')

                    logger.info(f"[{self.source_name}] Found {len(cards)} cards on page {page_num}")

                    for card in cards:
                        try:
                            # Expanded Link Extractor
                            link_el = card.css('a[data-testid="listing-card-link"], a[href*="-20"], a[href*="domain.com.au"]')
                            if not link_el:
                                link_el = card.css('a[href]')
                            
                            link = ""
                            if link_el:
                                for a in link_el:
                                    href = a.attrib.get('href', '')
                                    if href and ("domain.com.au" in href or href.startswith("/")):
                                        link = href
                                        break

                            if link and not link.startswith("http"):
                                link = urljoin("https://www.domain.com.au", link)

                            if not link:
                                continue  # Skip cards without valid listing links

                            # Price
                            price_el = card.css('[data-testid="listing-card-price"]')
                            price = price_el[0].text.strip() if price_el else "Contact Agent"

                            # Address
                            addr_el = card.css('[data-testid="address"]')
                            address = addr_el[0].text.strip() if addr_el else f"{suburb.title()}, {state.upper()} {postcode}"

                            # Features
                            features = card.css('[data-testid="property-features-text-container"]')
                            beds, baths, cars = 0, 0, 0
                            for feat in features:
                                text = feat.text.lower()
                                digits = ''.join(filter(str.isdigit, text)) or '0'
                                if "bed" in text:
                                    beds = int(digits)
                                elif "bath" in text:
                                    baths = int(digits)
                                elif "parking" in text or "car" in text:
                                    cars = int(digits)

                            item = PropertyListing(
                                source=self.source_name,
                                address=address,
                                suburb=suburb,
                                state=state,
                                postcode=postcode,
                                price=price,
                                bedrooms=beds,
                                bathrooms=baths,
                                car_spaces=cars,
                                url=link,
                            )
                            listings.append(item)
                        except Exception as parse_err:
                            logger.warning(f"[{self.source_name}] Error parsing card: {parse_err}")

                    time.sleep(2)
                except Exception as e:
                    logger.error(f"[{self.source_name}] Failed page {page_num}: {e}")
                    break

        return listings

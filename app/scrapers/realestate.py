import time
from typing import List
from urllib.parse import urljoin
from scrapling.fetchers import StealthySession
from app.models.property import PropertyListing
from app.scrapers.base import BasePropertyScraper
from app.utils.logger import logger


class RealestateComAuScraper(BasePropertyScraper):
    source_name: str = "realestate.com.au"

    def scrape_suburb(
        self, suburb: str, state: str, postcode: str, max_pages: int = 1
    ) -> List[PropertyListing]:
        listings: List[PropertyListing] = []
        suburb_slug = f"{suburb.lower().replace(' ', '-')}+{state.lower()}+{postcode}"
        base_url = f"https://www.realestate.com.au/buy/in-{suburb_slug}"

        logger.info(f"[{self.source_name}] Starting suburb scrape for {suburb_slug}")

        with StealthySession(headless=self.headless, real_chrome=True) as session:
            for page_num in range(1, max_pages + 1):
                url = f"{base_url}/list-{page_num}" if page_num > 1 else f"{base_url}/list-1"
                logger.info(f"[{self.source_name}] Fetching page {page_num}: {url}")

                try:
                    page = session.fetch(
                        url,
                        wait_selector="div.results-tier, article, div.residential-card",
                        wait=3500,
                        network_idle=True,
                    )

                    if page.status != 200:
                        logger.error(f"[{self.source_name}] Page {page_num} returned HTTP {page.status}")
                        break

                    cards = page.css("article.aria-title-mask, article[class*='residential-card'], div.residential-card")
                    logger.info(f"[{self.source_name}] Found {len(cards)} cards on page {page_num}")

                    for card in cards:
                        try:
                            # Link
                            link_el = card.css("a.details-link, a[href*='/property-']")
                            link = link_el[0].attrib.get("href", "") if link_el else ""
                            if link and not link.startswith("http"):
                                link = urljoin("https://www.realestate.com.au", link)

                            if not link:
                                continue

                            # Price
                            price_el = card.css("span.property-price, [class*='property-price']")
                            price = price_el[0].text.strip() if price_el else "Contact Agent"

                            # Address
                            addr_el = card.css("a.address-single, [class*='address']")
                            address = addr_el[0].text.strip() if addr_el else f"{suburb.title()}, {state.upper()} {postcode}"

                            # Features
                            feature_items = card.css("ul li, [class*='general-features'] span")
                            beds, baths, cars = 0, 0, 0
                            for item_el in feature_items:
                                aria_label = item_el.attrib.get("aria-label", "").lower()
                                text = (aria_label or item_el.text).lower()
                                digits = ''.join(filter(str.isdigit, text)) or '0'
                                if "bedroom" in text or "bed" in text:
                                    beds = int(digits)
                                elif "bathroom" in text or "bath" in text:
                                    baths = int(digits)
                                elif "parking" in text or "car" in text:
                                    cars = int(digits)

                            listing = PropertyListing(
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
                            listings.append(listing)
                        except Exception as parse_err:
                            logger.warning(f"[{self.source_name}] Error parsing card: {parse_err}")

                    time.sleep(2)
                except Exception as e:
                    logger.error(f"[{self.source_name}] Failed page {page_num}: {e}")
                    break

        return listings

import re
from typing import List
from loguru import logger
from app.models.property import PropertyListing
from app.scrapers.base import BasePropertyScraper


class RealEstateAuScraper(BasePropertyScraper):
    source_name = "realestate.com.au"
    BASE_URL = "https://www.realestate.com.au"

    def scrape_suburb(self, suburb: str, state: str, postcode: str, max_pages: int = 1) -> List[PropertyListing]:
        results: List[PropertyListing] = []
        formatted_suburb = f"{suburb.lower().replace(' ', '-')}-{state.lower()}-{postcode}"

        for page_num in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/buy/in-{formatted_suburb}/list-{page_num}"
            page = self.fetch_page(url)

            if not page:
                break

            card_elements = page.css("article.residential-card, div.tier2-container", auto_save=True)

            if not card_elements:
                logger.warning(f"[{self.source_name}] No cards found on page {page_num} for {formatted_suburb}")
                break

            for card in card_elements:
                try:
                    link_el = card.css("a.card-image-link::attr(href), a[href*='/property-']::attr(href)").first
                    relative_url = link_el.text if link_el else ""
                    full_url = f"{self.BASE_URL}{relative_url}" if relative_url.startswith('/') else relative_url

                    listing_id_match = re.search(r'-(\d+)$', relative_url)
                    listing_id = listing_id_match.group(1) if listing_id_match else full_url

                    price = card.css(".property-price").text or "Contact Agent"
                    address = card.css(".address").text or f"{suburb}, {state} {postcode}"

                    beds = card.css(".property-feature__feature[aria-label*='bedroom']").text
                    baths = card.css(".property-feature__feature[aria-label*='bathroom']").text
                    cars = card.css(".property-feature__feature[aria-label*='parking']").text

                    listing = PropertyListing(
                        id=f"rea-{listing_id}",
                        source=self.source_name,
                        url=full_url or "https://www.realestate.com.au",
                        address=address,
                        suburb=suburb.title(),
                        state=state.upper(),
                        postcode=postcode,
                        price_text=price,
                        bedrooms=int(beds) if beds and beds.isdigit() else None,
                        bathrooms=int(baths) if baths and baths.isdigit() else None,
                        car_spaces=int(cars) if cars and cars.isdigit() else None,
                    )
                    results.append(listing)
                except Exception as err:
                    logger.warning(f"[{self.source_name}] Failed to parse card: {err}")
                    continue

        return results

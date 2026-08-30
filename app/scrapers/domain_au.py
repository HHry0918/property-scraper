import json
import re
from typing import List
from loguru import logger
from app.models.property import PropertyListing
from app.scrapers.base import BasePropertyScraper


class DomainAuScraper(BasePropertyScraper):
    source_name = "domain.com.au"
    BASE_URL = "https://www.domain.com.au"

    def scrape_suburb(self, suburb: str, state: str, postcode: str, max_pages: int = 1) -> List[PropertyListing]:
        results: List[PropertyListing] = []
        formatted_suburb = f"{suburb.lower().replace(' ', '-')}-{state.lower()}-{postcode}"

        for page_num in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/sale/{formatted_suburb}/?page={page_num}"
            page = self.fetch_page(url)

            if not page:
                break

            # Method A: Try JSON Extraction from __NEXT_DATA__ script tag
            next_data_script = page.css("script#__NEXT_DATA__::text").first
            if next_data_script:
                try:
                    data = json.loads(next_data_script.text)
                    page_props = data.get("props", {}).get("pageProps", {})
                    listings_data = page_props.get("componentProps", {}).get("listingsMap", {})

                    if not listings_data:
                        # Fallback for alternative Next.js schema structure
                        search_results = page_props.get("searchResults", {})
                        listings_data = search_results.get("listings", [])

                    if isinstance(listings_data, dict):
                        listings_data = list(listings_data.values())

                    for item in listings_data:
                        listing_info = item.get("listing") or item
                        if not isinstance(listing_info, dict):
                            continue

                        listing_id = str(listing_info.get("id", ""))
                        if not listing_id:
                            continue

                        price = listing_info.get("price") or listing_info.get("priceDetails", {}).get("displayPrice")
                        address = listing_info.get("addressParts", {}).get("displayAddress")
                        media = listing_info.get("media", [])
                        image_url = media[0].get("url") if media and isinstance(media, list) else None

                        listing = PropertyListing(
                            id=f"dom-{listing_id}",
                            source=self.source_name,
                            url=f"{self.BASE_URL}/{listing_id}",
                            address=address or f"{suburb}, {state} {postcode}",
                            suburb=suburb.title(),
                            state=state.upper(),
                            postcode=postcode,
                            price_text=str(price) if price else "Contact Agent",
                            bedrooms=listing_info.get("beds"),
                            bathrooms=listing_info.get("baths"),
                            car_spaces=listing_info.get("parking"),
                            image_url=image_url,
                        )
                        results.append(listing)

                    if results:
                        logger.info(f"[{self.source_name}] Successfully parsed {len(results)} listings via JSON state.")
                        continue
                except Exception as json_err:
                    logger.warning(f"[{self.source_name}] Failed to parse __NEXT_DATA__: {json_err}")

            # Method B: Direct DOM CSS Query Fallback
            card_elements = page.css("ul[data-testid='results'] > li, div[data-testid='listing-card']", auto_save=True)
            for card in card_elements:
                try:
                    link_el = card.css("a::attr(href)").first
                    full_url = link_el.text if link_el else ""
                    if not full_url:
                        continue

                    listing_id_match = re.search(r'-(\d+)$', full_url)
                    listing_id = listing_id_match.group(1) if listing_id_match else full_url

                    price = card.css("[data-testid='listing-card-price']").text
                    address = card.css("[data-testid='address-line1']").text

                    listing = PropertyListing(
                        id=f"dom-{listing_id}",
                        source=self.source_name,
                        url=full_url if full_url.startswith("http") else f"{self.BASE_URL}{full_url}",
                        address=address or f"{suburb}, {state}",
                        suburb=suburb.title(),
                        state=state.upper(),
                        postcode=postcode,
                        price_text=price,
                    )
                    results.append(listing)
                except Exception as err:
                    continue

        return results

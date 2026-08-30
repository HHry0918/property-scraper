import json
from pathlib import Path
from typing import List

from app.models.property import PropertyListing
from app.scrapers.domain import DomainScraper
from app.scrapers.realestate import RealestateComAuScraper
from app.utils.logger import logger


def run_pipeline(
    suburb: str = "Sydney",
    state: str = "NSW",
    postcode: str = "2000",
    max_pages: int = 1,
    output_file: str = "output_listings.json",
) -> List[PropertyListing]:
    logger.info("Initializing property scrapers pipeline...")

    scrapers = [
        DomainScraper(),
        RealestateComAuScraper(),
    ]

    all_listings: List[PropertyListing] = []

    for scraper in scrapers:
        logger.info(f"Executing scraper: {scraper.source_name}")
        try:
            results = scraper.scrape_suburb(
                suburb=suburb,
                state=state,
                postcode=postcode,
                max_pages=max_pages,
            )
            logger.info(f"[{scraper.source_name}] Successfully scraped {len(results)} listings.")
            all_listings.extend(results)
        except Exception as e:
            logger.error(f"Execution error for scraper {scraper.source_name}: {e}")

    logger.info(f"Pipeline completed. Total listings collected: {len(all_listings)}")

    output_path = Path(output_file)
    data = [listing.model_dump() for listing in all_listings]
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info(f"Saved results to {output_path.resolve()}")

    return all_listings


if __name__ == "__main__":
    run_pipeline()

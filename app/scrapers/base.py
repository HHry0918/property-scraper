import os
import time
from abc import ABC, abstractmethod
from typing import List, Optional
from scrapling.fetchers import StealthyFetcher
from app.models.property import PropertyListing
from app.utils.logger import logger


class BasePropertyScraper(ABC):
    source_name: str = "base"

    def __init__(self, adaptive: bool = True, headless: Optional[bool] = None):
        StealthyFetcher.adaptive = adaptive
        if headless is None:
            self.headless = os.getenv("HEADLESS", "false").lower() == "true"
        else:
            self.headless = headless

    def fetch_page(
        self,
        url: str,
        wait_selector: Optional[str] = None,
        retries: int = 3,
        backoff: float = 3.0,
    ) -> Optional[object]:
        fetch_kwargs = {
            "headless": self.headless,
            "real_chrome": True,
            "network_idle": True,
            "block_ads": True,
            "wait": 3000,
        }

        if wait_selector:
            fetch_kwargs["wait_selector"] = wait_selector

        for attempt in range(1, retries + 1):
            try:
                logger.info(f"[{self.source_name}] Stealth fetch (Attempt {attempt}/{retries}): {url}")
                page = StealthyFetcher.fetch(url, **fetch_kwargs)

                if page.status == 200:
                    return page
                elif page.status in (429, 403):
                    logger.warning(
                        f"[{self.source_name}] HTTP {page.status} (Challenge/Block). Retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.error(f"[{self.source_name}] HTTP status {page.status} for {url}")
                    break
            except Exception as e:
                logger.error(f"[{self.source_name}] Request error on attempt {attempt}: {e}")
                time.sleep(backoff)
                backoff *= 2

        return None

    @abstractmethod
    def scrape_suburb(
        self, suburb: str, state: str, postcode: str, max_pages: int = 1
    ) -> List[PropertyListing]:
        pass

# property-scraper

## Folder structure
property-scraper/
├── .gitignore                   # Git exclusion rules (env, pycache, logs, output)
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── property.py          # PropertyListing Pydantic schema
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py              # Base scraper class
│   │   ├── domain.py            # Domain scraper
│   │   ├── realestate.py        # Realestate scraper
│   │   └── pipeline.py          # Pipeline runner
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # Centralized Loguru logger
├── logs/                        # Ignored by git
│   └── scraper.log
├── output_listings.json         # Ignored by git
├── pyproject.toml
└── README.md

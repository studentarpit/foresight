# Curated 20-stock universe across 6 high-growth Indian sectors.
# ticker: NSE symbol without .NS suffix
# mcap_category: Small (<2000Cr) | Mid (2000-20000Cr) | Large (>20000Cr)
STOCK_UNIVERSE = [
    # Defence
    {
        "ticker": "BEL", "name": "Bharat Electronics Ltd", "sector": "Defence",
        "mcap_category": "Large", "bse_code": "500049", "isin": "INE263A01024",
        "ir_url": "https://bel-india.in/investor-relations",
    },
    {
        "ticker": "MAZDOCK", "name": "Mazagon Dock Shipbuilders Ltd", "sector": "Defence",
        "mcap_category": "Large", "bse_code": "543237", "isin": "INE249Z01012",
        "ir_url": "https://mazagondock.in/investor-relations",
    },
    {
        "ticker": "HAL", "name": "Hindustan Aeronautics Ltd", "sector": "Defence",
        "mcap_category": "Large", "bse_code": "541154", "isin": "INE066F01020",
        "ir_url": "https://hal-india.co.in/investor-relations",
    },
    {
        "ticker": "BHEL", "name": "Bharat Heavy Electricals Ltd", "sector": "Defence",
        "mcap_category": "Large", "bse_code": "500103", "isin": "INE257A01026",
        "ir_url": "https://bhel.com/investor-relations",
    },
    {
        "ticker": "PARAS", "name": "Paras Defence and Space Technologies", "sector": "Defence",
        "mcap_category": "Small", "bse_code": "543366", "isin": "INE376R01022",
        "ir_url": "https://parasdefence.com/investor-relations",
    },
    # Railways
    {
        "ticker": "RVNL", "name": "Rail Vikas Nigam Ltd", "sector": "Railways",
        "mcap_category": "Large", "bse_code": "542649", "isin": "INE415G01027",
        "ir_url": "https://rvnl.org/investor-information",
    },
    {
        "ticker": "TITAGARH", "name": "Titagarh Rail Systems Ltd", "sector": "Railways",
        "mcap_category": "Mid", "bse_code": "540611", "isin": "INE322K01021",
        "ir_url": "https://titagarhrailsystems.com/investors",
    },
    {
        "ticker": "JWL", "name": "Jupiter Wagons Ltd", "sector": "Railways",
        "mcap_category": "Mid", "bse_code": "543564", "isin": "INE174P01019",
        "ir_url": "https://jupiterwagons.com/investors",
    },
    # EPC
    {
        "ticker": "KPIL", "name": "Kalpataru Projects International Ltd", "sector": "EPC",
        "mcap_category": "Mid", "bse_code": "522287", "isin": "INE220B01022",
        "ir_url": "https://kalpataruprojects.com/investors",
    },
    {
        "ticker": "KECL", "name": "KEC International Ltd", "sector": "EPC",
        "mcap_category": "Mid", "bse_code": "532714", "isin": "INE389H01022",
        "ir_url": "https://kecrpg.com/investors",
    },
    {
        "ticker": "TECHNOE", "name": "Techno Electric & Engineering Co Ltd", "sector": "EPC",
        "mcap_category": "Mid", "bse_code": "542066", "isin": "INE285K01026",
        "ir_url": "https://technoelectric.com/investor-relations",
    },
    # EMS
    {
        "ticker": "KAYNES", "name": "Kaynes Technology India Ltd", "sector": "EMS",
        "mcap_category": "Mid", "bse_code": "543228", "isin": "INE918Z01022",
        "ir_url": "https://kaynes.in/investor-relations",
    },
    {
        "ticker": "SYRMA", "name": "Syrma SGS Technology Ltd", "sector": "EMS",
        "mcap_category": "Mid", "bse_code": "543573", "isin": "INE900V01019",
        "ir_url": "https://syrmasgs.com/investors",
    },
    {
        "ticker": "DIXON", "name": "Dixon Technologies (India) Ltd", "sector": "EMS",
        "mcap_category": "Large", "bse_code": "541403", "isin": "INE935N01020",
        "ir_url": "https://dixoninfo.com/investor-relations",
    },
    # Power
    {
        "ticker": "TRIL", "name": "Transformers and Rectifiers India Ltd", "sector": "Power",
        "mcap_category": "Mid", "bse_code": "539960", "isin": "INE429V01022",
        "ir_url": "https://trilindia.com/investors",
    },
    {
        "ticker": "POWERINDIA", "name": "Hitachi Energy India Ltd", "sector": "Power",
        "mcap_category": "Large", "bse_code": "543213", "isin": "INE878B01027",
        "ir_url": "https://hitachienergy.com/in/investors",
    },
    {
        "ticker": "CESC", "name": "CESC Ltd", "sector": "Power",
        "mcap_category": "Mid", "bse_code": "500084", "isin": "INE486A01013",
        "ir_url": "https://cesc.co.in/investor-relations",
    },
    # Solar/Wind
    {
        "ticker": "WAAREEENER", "name": "Waaree Energies Ltd", "sector": "Solar/Wind",
        "mcap_category": "Large", "bse_code": "544268", "isin": "INE01RL01021",
        "ir_url": "https://waaree.com/investors",
    },
    {
        "ticker": "INOXWIND", "name": "Inox Wind Ltd", "sector": "Solar/Wind",
        "mcap_category": "Mid", "bse_code": "539083", "isin": "INE066Q01021",
        "ir_url": "https://inoxwind.com/investor-relations",
    },
    {
        "ticker": "STERLINWILSN", "name": "Sterling and Wilson Renewable Energy", "sector": "Solar/Wind",
        "mcap_category": "Mid", "bse_code": "542760", "isin": "INE901X01018",
        "ir_url": "https://sterlingandwilson.com/investor-relations",
    },
]


def get_tickers() -> list:
    """Return list of all NSE tickers (without .NS suffix)."""
    return [s["ticker"] for s in STOCK_UNIVERSE]


def get_by_sector(sector: str) -> list:
    """Return stocks filtered by sector name."""
    return [s for s in STOCK_UNIVERSE if s["sector"] == sector]


def get_sectors() -> list:
    """Return sorted list of unique sector names."""
    return sorted(set(s["sector"] for s in STOCK_UNIVERSE))


def get_stock_meta(ticker: str) -> dict:
    """Return full metadata dict for a ticker, or empty dict."""
    for s in STOCK_UNIVERSE:
        if s["ticker"] == ticker:
            return s
    return {}

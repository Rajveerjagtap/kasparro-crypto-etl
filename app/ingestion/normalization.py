from typing import Dict, Optional
import difflib
import logging

logger = logging.getLogger(__name__)

class SymbolNormalizer:
    """
    Normalizes crypto symbols using exact matching and fuzzy fallback.
    """
    
    # Canonical mapping: Input -> Canonical Symbol
    # This could be loaded from a DB or config file in production
    CANONICAL_MAP = {
        "bitcoin": "BTC",
        "btc": "BTC",
        "ethereum": "ETH",
        "eth": "ETH",
        "solana": "SOL",
        "sol": "SOL",
        "cardano": "ADA",
        "ada": "ADA",
        "ripple": "XRP",
        "xrp": "XRP",
        "polkadot": "DOT",
        "dot": "DOT",
        "dogecoin": "DOGE",
        "doge": "DOGE"
    }

    # List of valid canonical symbols
    VALID_SYMBOLS = sorted(list(set(CANONICAL_MAP.values())))

    def __init__(self):
        pass

    def normalize(self, input_symbol: str) -> Optional[str]:
        """
        Normalize a symbol string to its canonical form.
        1. Exact match (case-insensitive)
        2. Fuzzy match against known keys
        """
        if not input_symbol:
            return None

        cleaned = input_symbol.lower().strip()

        # 1. Exact match
        if cleaned in self.CANONICAL_MAP:
            return self.CANONICAL_MAP[cleaned]

        # 2. Check if it's already a valid canonical symbol
        upper_cleaned = cleaned.upper()
        if upper_cleaned in self.VALID_SYMBOLS:
            return upper_cleaned

        # 3. Fuzzy match
        # We match against the keys of our map to find the likely intent
        keys = list(self.CANONICAL_MAP.keys())
        matches = difflib.get_close_matches(cleaned, keys, n=1, cutoff=0.8)
        
        if matches:
            match = matches[0]
            canonical = self.CANONICAL_MAP[match]
            logger.info(f"Fuzzy mapped '{input_symbol}' to '{canonical}' (match: '{match}')")
            return canonical

        logger.warning(f"Could not normalize symbol: '{input_symbol}'")
        return None

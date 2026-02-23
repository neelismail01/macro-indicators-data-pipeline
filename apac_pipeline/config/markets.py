MARKET_METADATA: dict[str, dict] = {
    "JP": {
        "calendar": "XTKS",
        "currency": "JPY",
        "timezone": "Asia/Tokyo",
    },
    "HK": {
        "calendar": "XHKG",
        "currency": "HKD",
        "timezone": "Asia/Hong_Kong",
    },
    "KR": {
        "calendar": "XKRX",
        "currency": "KRW",
        "timezone": "Asia/Seoul",
    },
    "TW": {
        "calendar": "XTAI",
        "currency": "TWD",
        "timezone": "Asia/Taipei",
    },
}

MACRO_INDICATORS: dict[str, dict[str, dict]] = {
    "JP": {
        "FX_VS_USD":      {"ticker": "DEXJPUS", "source": "fred"},
        "POLICY_RATE":    {"ticker": "IRSTCI01JPM156N", "source": "fred"},
        "INFLATION_CPI":  {"ticker": "JPNCPIALLMINMEI", "source": "fred"},
        "BOND_YIELD_10Y": {"ticker": "IRLTLT01JPM156N", "source": "fred"},
        "EQUITY_INDEX":   {"ticker": "^N225", "source": "yfinance"},
    },
    "HK": {
        "FX_VS_USD":      {"ticker": "DEXHKUS", "source": "fred"},
        "POLICY_RATE":    {"ticker": "HKONGBASE", "source": "fred"},
        "INFLATION_CPI":  {"ticker": "HKGCPIALLMINMEI", "source": "fred"},
        "BOND_YIELD_10Y": {"ticker": "IRLTLT01HKM156N", "source": "fred"},
        "EQUITY_INDEX":   {"ticker": "^HSI", "source": "yfinance"},
    },
    "KR": {
        "FX_VS_USD":      {"ticker": "DEXKOUS", "source": "fred"},
        "POLICY_RATE":    {"ticker": "IRSTCI01KRM156N", "source": "fred"},
        "INFLATION_CPI":  {"ticker": "KORCPIALLMINMEI", "source": "fred"},
        "BOND_YIELD_10Y": {"ticker": "IRLTLT01KRM156N", "source": "fred"},
        "EQUITY_INDEX":   {"ticker": "^KS11", "source": "yfinance"},
    },
    "TW": {
        "FX_VS_USD":      {"ticker": "DEXTAUS", "source": "fred"},
        "POLICY_RATE":    {"ticker": "IRSTCI01TWM156N", "source": "fred"},
        "INFLATION_CPI":  {"ticker": "TWNCPIALLMINMEI", "source": "fred"},
        "BOND_YIELD_10Y": {"ticker": "IRLTLT01TWM156N", "source": "fred"},
        "EQUITY_INDEX":   {"ticker": "^TWII", "source": "yfinance"},
    },
}

INDICATOR_NAMES: list[str] = [
    "FX_VS_USD",
    "POLICY_RATE",
    "INFLATION_CPI",
    "BOND_YIELD_10Y",
    "EQUITY_INDEX",
]

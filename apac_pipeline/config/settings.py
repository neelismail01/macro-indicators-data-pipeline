from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

FRED_API_KEY: str = os.environ["FRED_API_KEY"]

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "apac_pipeline.duckdb"
RAW_DATA_PATH = BASE_DIR / "data" / "raw"
CLEAN_DATA_PATH = BASE_DIR / "data" / "cleaned"

START_DATE = "2015-01-01"

EQUITY_UNIVERSE: dict[str, list[str]] = {
    "JP": [
        "7203.T",  # Toyota
        "6758.T",  # Sony
        "9984.T",  # SoftBank
        "6861.T",  # Keyence
        "8306.T",  # Mitsubishi UFJ
        "9432.T",  # NTT
        "6954.T",  # Fanuc
        "4063.T",  # Shin-Etsu Chemical
        "8035.T",  # Tokyo Electron
        "7741.T",  # Hoya
    ],
    "HK": [
        "0700.HK",  # Tencent
        "0005.HK",  # HSBC
        "0941.HK",  # China Mobile
        "1299.HK",  # AIA
        "2318.HK",  # Ping An
        "0388.HK",  # HKEX
        "1177.HK",  # Sino Biopharmaceutical
        "2382.HK",  # Sunny Optical
        "0883.HK",  # CNOOC
        "1113.HK",  # CK Asset
    ],
    "KR": [
        "005930.KS",  # Samsung Electronics
        "000660.KS",  # SK Hynix
        "005380.KS",  # Hyundai Motor
        "035420.KS",  # NAVER
        "051910.KS",  # LG Chem
        "006400.KS",  # Samsung SDI
        "035720.KS",  # Kakao
        "028260.KS",  # Samsung C&T
        "012330.KS",  # Hyundai Mobis
        "096770.KS",  # SK Innovation
    ],
    "TW": [
        "2330.TW",  # TSMC
        "2317.TW",  # Foxconn
        "2454.TW",  # MediaTek
        "2412.TW",  # Chunghwa Telecom
        "2308.TW",  # Delta Electronics
        "1303.TW",  # Nan Ya Plastics
        "2881.TW",  # Fubon Financial
        "2882.TW",  # Cathay Financial
        "3008.TW",  # Largan Precision
        "2303.TW",  # United Microelectronics
    ],
}

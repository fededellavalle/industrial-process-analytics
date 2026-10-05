from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
CHARTS_DIR = BASE_DIR / "charts"
DB_PATH = DATA_DIR / "industrial_process.db"

RAW_FILE = RAW_DIR / "sensor_readings.csv"
PROCESSED_FILE = PROCESSED_DIR / "sensor_readings_processed.csv"

SAMPLE_ROWS = 20_000
RANDOM_SEED = 42

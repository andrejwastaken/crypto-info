import importlib.util
import os
from pathlib import Path
import pandas as pd

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    base_dir = Path(__file__).parent
    binance_path = base_dir / "binance-scraper.py"
    yfinance_path = base_dir / "yfinance-scraper.py"

    dfs = []

    # binance
    if binance_path.exists():
        try:
            binance_module = load_module("binance_scraper", binance_path)
            print("Running Binance Scraper...")
            df_binance = binance_module.scrape_binance_news()
            if not df_binance.empty:
                dfs.append(df_binance)
                print(f"Loaded {len(df_binance)} rows from Binance")
        except Exception as e:
            print(f"Error running Binance scraper: {e}")
    else:
        print(f"Warning: {binance_path} not found.")

    # yfinance
    if yfinance_path.exists():
        try:
            yfinance_module = load_module("yfinance_scraper", yfinance_path)
            print("Running YFinance Scraper...")
            df_yfinance = yfinance_module.scrape_yfinance_news()
            if not df_yfinance.empty:
                dfs.append(df_yfinance)
                print(f"Loaded {len(df_yfinance)} rows from YFinance")
        except Exception as e:
            print(f"Error running YFinance scraper: {e}")
    else:
        print(f"Warning: {yfinance_path} not found.")

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # ensure date column is consistent
        if 'date' in combined_df.columns:
            combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
            # sort by date descending
            combined_df = combined_df.sort_values(by='date', ascending=False)

        output_file = "news.csv"
        combined_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully combined {len(combined_df)} rows into {output_file}")
    else:
        print("\nNo data collected from any scraper.")

if __name__ == "__main__":
    main()

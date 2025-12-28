import importlib.util
from pathlib import Path
import pandas as pd

def load_module(name: str, path: Path):
    """dynamically load a python module from file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

def scrape_source(source_name: str, module_path: Path, scraper_func: str, light_mode: bool = False) -> pd.DataFrame:
    if not module_path.exists():
        print(f"Warning: {module_path} not found.")
        return pd.DataFrame()
    
    try:
        module = load_module(f"{source_name.lower()}_scraper", module_path)
        print(f"\nRunning {source_name} Scraper...")
        
        scrape_function = getattr(module, scraper_func)
        try:
            df = scrape_function(light_mode=light_mode)
        except TypeError:
            print(f"Warning: {source_name} scraper does not support light_mode. Running default.")
            df = scrape_function()
        
        if not df.empty:
            print(f"Loaded {len(df)} rows from {source_name}")
            return df
        else:
            print(f"No data returned from {source_name}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error running {source_name} scraper: {e}")
        return pd.DataFrame()


def scrape_all_news(light_mode: bool = False) -> pd.DataFrame:
    """
    scrape news from all available sources and combine into single dataframe.
    """
    base_dir = Path(__file__).parent
    
    # define scrapers
    scrapers = [
        # ("Binance", base_dir / "binance-scraper.py", "scrape_binance_news"),
        ("YFinance", base_dir / "yfinance-scraper.py", "scrape_yfinance_news"),
        ("Coindesk", base_dir / "coindesk-scraper.py", "scrape_coindesk_news"),
    ]
    
    # scrape all sources
    dataframes = []
    for source_name, module_path, func_name in scrapers:
        df = scrape_source(source_name, module_path, func_name, light_mode=light_mode)
        if not df.empty:
            dataframes.append(df)
    
    # combine results
    if not dataframes:
        print("\nNo data collected from any scraper.")
        return pd.DataFrame()
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # standardize date column
    if 'date' in combined_df.columns:
        combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
        combined_df = combined_df.sort_values(by='date', ascending=False)
    
    print(f"\nSuccessfully combined {len(combined_df)} rows from all sources")
    return combined_df

def main():
    # run this for testing purposes
    df = scrape_all_news()
    if not df.empty:
        output_file = "news.csv"
        df.to_csv(output_file, index=False)
        print(f"\nSaved to {output_file}")
    else:
        print("\nNo data to save.")


if __name__ == "__main__":
    main()
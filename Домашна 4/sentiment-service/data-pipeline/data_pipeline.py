"""Main pipeline execution for cryptocurrency data collection."""

import multiprocessing
import time

import pandas as pd

from filters import Filter, Filter1, Filter2, Filter3, Filter4


def run_pipeline() -> pd.DataFrame:
    """
    Execute the complete data pipeline using pipe-and-filter architecture.
    
    Pipeline stages:
    1. Filter1: Scrape top cryptocurrencies from Yahoo Finance
    2. Filter2: Download historical data for new coins
    3. Filter3: Update existing coins with recent data
    4. Filter4: Save all data to database
    
    Returns:
        Final DataFrame with processed metadata
    """
    print("=" * 60)
    print("Starting Cryptocurrency Data Pipeline")
    print("=" * 60)
    
    start_time = time.time()
    
    # Get all registered filter classes sorted by order
    filter_classes = sorted(
        Filter.__subclasses__(), 
        key=lambda f: getattr(f, 'order', 999)
    )
    
    # Execute pipeline
    df = pd.DataFrame()
    for filter_cls in filter_classes:
        filter_instance = filter_cls()
        df = filter_instance.apply(df)
        print()  # Add spacing between filters
    
    elapsed = time.time() - start_time
    
    print("=" * 60)
    print(f"Pipeline Complete!")
    print(f"Total execution time: {elapsed:.2f} seconds")
    print(f"Final dataset: {len(df)} coins")
    print("=" * 60)
    
    return df


def main():
    """Entry point for the data pipeline."""
    multiprocessing.freeze_support()
    run_pipeline()


if __name__ == "__main__":
    main()

import subprocess
import pandas as pd
import os
import sys
import time

def run_scraper(script_name):
    print(f"Starting {script_name}...")
    try:
        # Run the script using the current python executable
        process = subprocess.Popen(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        print(f"Failed to start {script_name}: {e}")
        return None

def main():
    scripts = ["binance-scraper.py", "yfinance-scraper.py"]
    processes = []

    # start processes in parallel
    for script in scripts:
        if os.path.exists(script):
            p = run_scraper(script)
            if p:
                processes.append((script, p))
        else:
            print(f"Script {script} not found!")

    # wait for completion and collect output
    for script, p in processes:
        stdout, stderr = p.communicate()
        print(f"\n--- Output from {script} ---")
        print(stdout)
        if stderr:
            print(f"--- Errors from {script} ---")
            print(stderr)
        print(f"{script} finished with return code {p.returncode}")

    # combine results
    csv_files = ["binance-news.csv", "yfinance-news.csv"]
    dfs = []

    for csv_file in csv_files:
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                dfs.append(df)
                print(f"Loaded {len(df)} rows from {csv_file}")
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
        else:
            print(f"Warning: {csv_file} not found. It might not have been generated.")

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
        print(combined_df.head())
    else:
        print("\nNo data collected from any scraper.")

if __name__ == "__main__":
    main()

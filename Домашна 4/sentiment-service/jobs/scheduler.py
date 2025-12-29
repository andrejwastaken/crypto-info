import schedule
import time
import sys
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
pipeline_path = os.path.join(ROOT_DIR, 'data-pipeline')
technical_path = os.path.join(ROOT_DIR, 'technical-analysis')
lstm_path = os.path.join(ROOT_DIR, 'lstm') 

sys.path.append(pipeline_path)
sys.path.append(technical_path)
sys.path.append(lstm_path)

try:
    from data_pipeline import run_pipeline as start_crypto_pipeline
    from combine_signals import main as start_technical_analysis 
  
    #from predictions import LSTMPredictionStrategy, PredictionService
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}", flush=True)
    sys.exit(1)

# def start_lstm_prediction():
#     print(f"[{datetime.now()}] Starting LSTM Prediction...", flush=True)
#     try:
#         lstm_strategy = LSTMPredictionStrategy()
#         service = PredictionService(lstm_strategy)
#         service.run()
#         print(f"[{datetime.now()}] LSTM Prediction Complete.", flush=True)
#     except Exception as e:
#         print(f"LSTM Prediction Failed: {e}", flush=True)

def run_sequence():
    print(f"\n{'='*20}")
    print(f"SEQUENCE STARTED AT {datetime.now()}")
    print(f"{'='*20}")

    
    print(f"[{datetime.now()}] Starting Crypto Data Pipeline...", flush=True)
    try:
        start_crypto_pipeline()
        print(f"[{datetime.now()}] Complete.", flush=True)
    except Exception as e:
        print(f"Failed: {e}. Sequence aborted.", flush=True)
        return 

    
    print(f"\n[{datetime.now()}] Starting Technical Analysis...", flush=True)
    try:
        start_technical_analysis()
        print(f"[{datetime.now()}] Complete.", flush=True)
    except Exception as e:
        print(f"Failed: {e}", flush=True)


    # print(f"\n[{datetime.now()}] Starting LSTM Analysis...", flush=True)
    # start_lstm_prediction()

    print(f"\n{'='*20}")
    print(f"SEQUENCE FINISHED AT {datetime.now()}")
    print(f"{'='*20}\n", flush=True)

def start_scheduler():
   
    schedule.every().day.at("08:00").do(run_sequence)
    
    print("="*40)
    print(f"SCHEDULER LOOP STARTED AT {datetime.now().strftime('%H:%M:%S')}")
    print("="*40, flush=True)

    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    start_scheduler()
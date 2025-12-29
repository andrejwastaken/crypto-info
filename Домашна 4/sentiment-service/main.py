import sys
from pathlib import Path
from fastapi import FastAPI, Request
import uvicorn
import time
import asyncio
import httpx
from dotenv import load_dotenv
import os
import threading
from datetime import datetime



scrapers_path = Path(__file__).parent/ "sentiment-analysis" / "scrapers"
analysis_path = Path(__file__).parent/ "sentiment-analysis" / "analysis"
sys.path.append(str(scrapers_path))
sys.path.append(str(analysis_path))

load_dotenv()

CALLBACK_TOKEN = os.getenv("CALLBACK_SECRET_TOKEN")

try:
    from sentiment_analysis import run_pipeline
    from jobs.scheduler import start_scheduler
except ImportError as e:
    print(f"IMPORTING ERROR {e}")
    run_pipeline = None

if CALLBACK_TOKEN is None or CALLBACK_TOKEN == '':
    raise Exception("No callback token.")

app = FastAPI()

@app.post("/api/update-sentiment", status_code=202)
async def get_news_sentiment(request: Request):
    if not run_pipeline:
        return {"error": "Sentiment analysis pipeline not available"}
    
    try:
        data = await request.json()
        callback_url = data.get("callbackUrl")
        
        if not callback_url:
            return {"error": "callbackUrl is required"}

        asyncio.create_task(run_sentiment_pipeline(callback_url))
        
        return {"status": "accepted"}
    except Exception as e:
        return {"error": "Failed to process request"}

async def run_sentiment_pipeline(callback_url: str):
    print('Starting sentiment analysis pipeline...')
    pipeline_success = False
    try:
        run_pipeline()
        pipeline_success = True
        print('Sentiment analysis pipeline completed.')
    except Exception as e:
        print(f"Error in sentiment pipeline: {e}")
    async with httpx.AsyncClient() as client:
        print(f'Sending callback to {callback_url}')
        headers = {
            "X-Secret-Token": CALLBACK_TOKEN  
        }
        await client.post(
                callback_url, 
                json={"success": pipeline_success},
                headers=headers
            )

# @app.post("/api/test", status_code=202)
# async def test_route(request: Request):
#     data = await request.json()
#     callback_url = data.get("callbackUrl")
    
#     if callback_url:
#         # schedule callback 
#         asyncio.create_task(send_callback(callback_url, data))
    
#     return {"status": "accepted"}

# async def send_callback(callback_url: str, data: dict):
#     print('starting job...')
#     # simulate long running task
#     await asyncio.sleep(5)
#     try:
#         async with httpx.AsyncClient() as client:
#             print('sending request now.')
#             await client.post(callback_url, json=data)
#     except Exception as e:
#         print(f"Error sending callback: {e}")



# Check if the scheduler thread exists and is alive

# @app.get("/api/health")
# async def health_check():
#     scheduler_alive = False
#     for thread in threading.enumerate():
#         if thread.name == "SchedulerThread" and thread.is_alive():
#             scheduler_alive = True
#             break
            
#     return {
#         "status": "online",
#         "scheduler_running": scheduler_alive,
#         "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     }


if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=start_scheduler,name="SchedulerThread", daemon=True)
    scheduler_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
   

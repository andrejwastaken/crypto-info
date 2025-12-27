import sys
from pathlib import Path
from fastapi import FastAPI, Request
import uvicorn
import time
import asyncio
import httpx

scrapers_path = Path(__file__).parent.parent / "sentiment-analysis" / "scrapers"
analysis_path = Path(__file__).parent.parent / "sentiment-analysis" / "analysis"
sys.path.append(str(scrapers_path))
sys.path.append(str(analysis_path))

try:
    from sentiment_analysis import run_pipeline
except ImportError as e:
    print(f"Error importing sentiment_analysis: {e}")
    run_pipeline = None

app = FastAPI()

@app.get("/api/light-sentiment")
async def get_news_sentiment():
    if not run_pipeline:
        return {"error": "Sentiment analysis pipeline not available"}
    
    try:
        df = run_pipeline(light_mode=True)
        
        if df is None or df.empty:
            return {"message": "No news found or pipeline stopped", "data": []}
            
        # Convert dataframe to list of dicts
        # Handle datetime serialization
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
            
        return {"data": df.to_dict(orient="records")}
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/test", status_code=202)
async def test_route(request: Request):
    data = await request.json()
    callback_url = data.get("callbackUrl")
    
    if callback_url:
        # schedule callback 
        asyncio.create_task(send_callback(callback_url, data))
    
    return {"status": "accepted"}

async def send_callback(callback_url: str, data: dict):
    print('starting job...')
    # simulate long running task
    await asyncio.sleep(5)
    try:
        async with httpx.AsyncClient() as client:
            print('sending request now.')
            await client.post(callback_url, json=data)
    except Exception as e:
        print(f"Error sending callback: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

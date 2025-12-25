import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn

scrapers_path = Path(__file__).parent.parent / "sentiment-analysis" / "scrapers"
sys.path.append(str(scrapers_path))

try:
    from scrapers_aggregator import scrape_all_news
except ImportError as e:
    print(f"Error importing scrapers: {e}")
    scrape_all_news = None

app = FastAPI()

@app.get("/api/light-sentiment")
async def get_news_sentiment():
    if not scrape_all_news:
        return {"error": "Scrapers not available"}
    
    try:
        df = scrape_all_news(light_mode=True)
        
        if df.empty:
            return {"message": "No news found", "data": []}
            
        # Convert dataframe to list of dicts
        # Handle datetime serialization
        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)
            
        return {"data": df.to_dict(orient="records")}
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

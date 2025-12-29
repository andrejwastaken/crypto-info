import os
import logging
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from urllib.parse import quote_plus
from typing import Tuple, List, Optional
from abc import ABC, abstractmethod
from torch.utils.data import DataLoader, TensorDataset
from dotenv import load_dotenv
from sqlalchemy import text
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score
import warnings
import sys
from pathlib import Path

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database.database import DatabaseManager


class Config:
   
    TABLE_NAME = 'ohlcv_predictions'
    # LSTM Hyperparameters
    HISTORY_LIMIT_DAYS = 4 * 365
    LOOKBACK_DAYS = 30
    BATCH_SIZE = 32
    EPOCHS = 100
    PATIENCE = 10
    LEARNING_RATE = 0.001
    TRAIN_SPLIT = 0.7
    
    @staticmethod
    def get_device():
        if torch.backends.mps.is_available(): return torch.device("mps")
        if torch.cuda.is_available(): return torch.device("cuda")
        return torch.device("cpu")



class DataRepository:
    def __init__(self):
        self.engine = DatabaseManager.get_engine()

    def init_table(self):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {Config.TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            predicted_close NUMERIC,
            predicted_change_pct NUMERIC
        );
        """
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()

    def get_symbols(self) -> List[str]:
        # Prioritize major coins
        return pd.read_sql("SELECT symbol FROM coins_metadata ORDER BY market_cap DESC", self.engine)['symbol'].tolist()

    def fetch_ohlcv(self, symbol: str) -> pd.DataFrame:
        query = text(f"""
            SELECT date, close FROM ohlcv_data
            WHERE symbol = :symbol AND date::DATE >= CURRENT_DATE - INTERVAL '{Config.HISTORY_LIMIT_DAYS} days'
            ORDER BY date ASC
        """)
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"symbol": symbol})
        
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.drop_duplicates(subset=["date"], keep="last").sort_values("date")
        return df

    def save_prediction(self, data: dict):
        # Remove old prediction for this date/symbol to avoid duplicates
        delete_sql = text(f"DELETE FROM {Config.TABLE_NAME} WHERE symbol = :sym AND date = :dt")
        with self.engine.connect() as conn:
            conn.execute(delete_sql, {"sym": data['symbol'][0], "dt": data['date'][0]})
            conn.commit()
        
        pd.DataFrame(data).to_sql(Config.TABLE_NAME, self.engine, if_exists='append', index=False)
        logger.info(f"Saved prediction for {data['symbol'][0]}: ${data['predicted_close'][0]:.4f}")

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        out, _ = self.lstm(x) 
        # Take the output of the last time step
        out = self.dropout(out[:, -1, :])
        return self.fc(out)

class PredictionStrategy(ABC):
    @abstractmethod
    def predict(self, df: pd.DataFrame, symbol: str) -> Optional[dict]:
        pass

class LSTMPredictionStrategy(PredictionStrategy):
    def __init__(self):
        self.device = Config.get_device()
        logger.info(f"LSTM Strategy initialized on: {self.device}")

    def _create_sequences(self, data: np.ndarray, seq_length: int) -> Tuple[np.ndarray, np.ndarray]:
        xs, ys = [], []
        for i in range(len(data) - seq_length):
            x = data[i:(i + seq_length)]
            y = data[i + seq_length]
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)

    def predict(self, df: pd.DataFrame, symbol: str) -> Optional[dict]:
        min_required = Config.LOOKBACK_DAYS + Config.BATCH_SIZE + 10
        if len(df) < min_required:
            logger.warning(f"Skipping {symbol}: Not enough data ({len(df)} rows).")
            return None

        # filter out coins with average close price <= 1.01
        avg_close = df['close'].mean()
        if avg_close <= 1.01:
            logger.info(f"Skipping {symbol}: Average close price too low ({avg_close:.4f})")
            return None

        scaler = MinMaxScaler(feature_range=(-1, 1))
        scaled_data = scaler.fit_transform(df['close'].values.reshape(-1, 1))

        X, y = self._create_sequences(scaled_data, Config.LOOKBACK_DAYS)
        
        split_idx = int(len(X) * Config.TRAIN_SPLIT)
        X_train_t = torch.tensor(X[:split_idx], dtype=torch.float32).to(self.device)
        y_train_t = torch.tensor(y[:split_idx], dtype=torch.float32).to(self.device)
        X_val_t = torch.tensor(X[split_idx:], dtype=torch.float32).to(self.device)
        y_val_t = torch.tensor(y[split_idx:], dtype=torch.float32).to(self.device)

        train_loader = DataLoader(TensorDataset(X_train_t, y_train_t), batch_size=Config.BATCH_SIZE, shuffle=True)

        model = LSTMModel().to(self.device)
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(model.parameters(), lr=Config.LEARNING_RATE)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)

        best_loss = float('inf')
        patience_counter = 0
        best_weights = None

        model.train()
        for epoch in range(Config.EPOCHS):
            for inputs, targets in train_loader:
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
            
            model.eval()
            with torch.no_grad():
                val_out = model(X_val_t)
                val_loss = criterion(val_out, y_val_t).item()
            model.train()
            
            scheduler.step(val_loss)

            if val_loss < best_loss:
                best_loss = val_loss
                best_weights = model.state_dict()
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= Config.PATIENCE:
                    break # Early stop
        
        if best_weights:
            model.load_state_dict(best_weights)
        
        model.eval()
        with torch.no_grad():
            preds_scaled = model(X_val_t).cpu().numpy()
            actuals_scaled = y_val_t.cpu().numpy()

        preds = scaler.inverse_transform(preds_scaled)
        actuals = scaler.inverse_transform(actuals_scaled)
        
        r2 = r2_score(actuals, preds)
        
        # Filter low accuracy models
        if r2 < 0.3:
            logger.info(f"Skipping {symbol}: R2 score too low ({r2:.4f})")
            return None

        last_seq = scaled_data[-Config.LOOKBACK_DAYS:]
        last_seq_t = torch.tensor(last_seq, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            future_scaled = model(last_seq_t).cpu().numpy()
        
        future_price = scaler.inverse_transform(future_scaled)[0][0]
        current_price = df['close'].iloc[-1]
        change_pct = ((future_price - current_price) / current_price) * 100

        return {
            'symbol': [symbol],
            'date': [pd.Timestamp.now().date() + pd.Timedelta(days=1)],
            'predicted_close': [float(future_price)],
            'predicted_change_pct': [float(change_pct)]
        }

class PredictionService:
    def __init__(self, strategy: PredictionStrategy):
        self.repo = DataRepository()
        self.strategy = strategy

    def run(self):
        self.repo.init_table()
        symbols = self.repo.get_symbols()
        logger.info(f"Starting analysis for {len(symbols)} symbols...")

        for symbol in symbols:
            try:
                df = self.repo.fetch_ohlcv(symbol)
                result = self.strategy.predict(df, symbol)
                if result:
                    self.repo.save_prediction(result)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
        
        logger.info("Batch processing complete.")

if __name__ == "__main__":
    lstm_strategy = LSTMPredictionStrategy()
    service = PredictionService(lstm_strategy)
    service.run()
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

import os
from pathlib import Path
from urllib.parse import quote_plus
import warnings

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import root_mean_squared_error, mean_absolute_percentage_error, r2_score

warnings.filterwarnings("ignore")
load_dotenv()

BASE_DIR = Path(__file__).parent
HISTORY_LIMIT_DAYS = 4 * 365 # 4 years is optimal for LSTM
LOOKBACK_DAYS = 30  # Window size for LSTM input
PREDICTION_DAYS = 1 # Days to predict ahead
BATCH_SIZE = 32 # Optimal batch size for training
EPOCHS = 100 # Will use early stopping
PATIENCE = 10 # Stop if no improvement after these many epochs
LEARNING_RATE = 0.001 # Optimal learning rate for Adam optimizer
TRAIN_SPLIT = 0.7 # 70% data for training, 30% for testing

# Device Configuration (Auto-detects M4 Pro GPU 'mps', NVIDIA 'cuda', or CPU)
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using Device: Apple MPS (M-Series GPU)")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print("Using Device: NVIDIA CUDA")
else:
    device = torch.device("cpu")
    print("Using Device: CPU")

_db_engine = None

def get_engine():
    global _db_engine
    
    if _db_engine is not None:
        return _db_engine
    
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_host, db_port, db_name]):
        raise RuntimeError("Database credentials are missing.")

    encoded_password = quote_plus(db_password)
    connection_str = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
    
    _db_engine = create_engine(connection_str, pool_size=10, max_overflow=20)
    return _db_engine

def init_db():
    engine = get_engine()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ohlcv_predictions (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        date DATE NOT NULL,
        predicted_close NUMERIC,
        predicted_change_pct NUMERIC
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    print("Database table 'ohlcv_predictions' checked/created.")

def get_all_symbols():
    engine = get_engine()
    # Ordering by market_cap ensures prioritization of major coins if script is stopped early
    query = "SELECT symbol FROM coins_metadata ORDER BY market_cap DESC"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df['symbol'].tolist()

def fetch_ohlcv_for_symbol(symbol):
    engine = get_engine()
    query = text(f"""
        SELECT date, close
        FROM ohlcv_data
        WHERE symbol = :symbol
          AND date::DATE >= CURRENT_DATE - INTERVAL '{HISTORY_LIMIT_DAYS} days'
        ORDER BY date ASC
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"symbol": symbol})
    
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates(subset=["date"], keep="last").sort_values("date")
    return df

def save_prediction(symbol, price, change_pct):
    engine = get_engine()
    
    # Target date is Tomorrow (relative to script execution time)
    prediction_date = pd.Timestamp.now().date() + pd.Timedelta(days=1)
    
    delete_query = text("DELETE FROM ohlcv_predictions WHERE symbol = :sym AND date = :dt")
    
    with engine.connect() as conn:
        conn.execute(delete_query, {"sym": symbol, "dt": prediction_date})
        conn.commit()

    data = {
        'symbol': [symbol],
        'date': [prediction_date],
        'predicted_close': [float(price)],
        'predicted_change_pct': [float(change_pct)]
    }
    pd.DataFrame(data).to_sql('ohlcv_predictions', engine, if_exists='append', index=False)
    print(f" -> Saved prediction for {symbol}: ${price:.4f} ({change_pct:.2f}%)")

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size = 64, num_layers = 2, output_size = 1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)

        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out)
        out = self.fc(out[:, -1, :])
        return out

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def process_symbol(symbol):
    print(f"\n--- Starting Analysis: {symbol} ---")

    df = fetch_ohlcv_for_symbol(symbol)
    # n_samples = total_rows - lookback_days
    # If you have 30-day windows 
    # and you want at least one full batch of 32 training examples 
    # you need 30 + 32 = 62 datapoints minimum. The +10 is just in case.
    min_required = LOOKBACK_DAYS + BATCH_SIZE + 10
    if len(df) < min_required:
        print(f"Skipping {symbol}: Insufficient data ({len(df)} rows).")
        return
    
    # Tanh and sigmoid activations work best with scaled data in range [-1, 1]
    scaler = MinMaxScaler(feature_range=(-1, 1))
    close_prices = df['close'].values.reshape(-1, 1)
    scaled_data = scaler.fit_transform(close_prices)

    X, y = create_sequences(scaled_data, LOOKBACK_DAYS)
    split_idx = int(len(X) * TRAIN_SPLIT)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    X_train_tensor = torch.tensor(X_train, dtype=torch.float32).to(device)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).to(device)
    X_val_tensor = torch.tensor(X_val, dtype=torch.float32).to(device)
    y_val_tensor = torch.tensor(y_val, dtype=torch.float32).to(device)

    train_loader = DataLoader(TensorDataset(X_train_tensor, y_train_tensor), batch_size=BATCH_SIZE, shuffle=True)

    model = LSTMModel().to(device)
    criterion = nn.MSELoss()
    # AdamW deals with weight decay better than standard Adam
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE) 
    # Reduce LR if validation loss plateaus
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)

    best_val_loss = float('inf')
    early_stop_counter = 0
    best_model_state = None
    
    for epoch in range(EPOCHS):
        model.train()
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
        
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_tensor)
            val_loss = criterion(val_outputs, y_val_tensor).item()
        
        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict() # Save best weights
            early_stop_counter = 0
        else:
            early_stop_counter += 1
            if early_stop_counter >= PATIENCE:
                print(f"Early stopping at epoch {epoch+1}. Best Val Loss: {best_val_loss:.6f}")
                break
        
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    
    model.eval()
    with torch.no_grad():
        val_preds_scaled = model(X_val_tensor).cpu().numpy()
        y_val_actual_scaled = y_val_tensor.cpu().numpy()
    
    val_preds = scaler.inverse_transform(val_preds_scaled)
    y_val_actual = scaler.inverse_transform(y_val_actual_scaled)

    rmse = root_mean_squared_error(y_val_actual, val_preds)
    mape = mean_absolute_percentage_error(y_val_actual, val_preds) * 100
    r2 = r2_score(y_val_actual, val_preds)

    print(f"Metrics -> RMSE: {rmse:.4f} | MAPE: {mape:.4f} | R2: {r2:.4f}")

    if r2 < 0.3:  # Arbitrary cutoff
        print(f"Skipping {symbol}: Model accuracy too low (R2: {r2:.4f})")
        return  

    # Use the very last 'window' of data from the entire dataset
    last_sequence = scaled_data[-LOOKBACK_DAYS:]
    last_sequence_t = torch.tensor(last_sequence, dtype=torch.float32).unsqueeze(0).to(device)
    
    with torch.no_grad():
        future_pred_scaled = model(last_sequence_t).cpu().numpy()
    
    future_price = scaler.inverse_transform(future_pred_scaled)[0][0]
    last_actual_price = df['close'].iloc[-1]
    change_pct = ((future_price - last_actual_price) / last_actual_price) * 100

    save_prediction(symbol, future_price, change_pct)

def main():
    try:
        init_db()
        
        symbols = get_all_symbols()
        print(f"Loaded {len(symbols)} symbols. Starting LSTM prediction...")
        
        for symbol in symbols:
            try:
                process_symbol(symbol)
            except KeyboardInterrupt:
                print("Process stopped by user.")
                break
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
                
        print("\n--- All Predictions Completed ---")
        
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()

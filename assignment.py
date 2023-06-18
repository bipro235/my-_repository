import requests
import pandas as pd
import mplfinance as mpf

class ScriptData:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def fetch_data(self, script):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={script}&interval=1min&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch intraday data for {script}. Error code: {response.status_code}")
    
    def __getitem__(self, script):
        if script in self.data:
            return self.data[script]
        else:
            print(f"No data available for {script}")
            return None
    
    def __setitem__(self, script, data):
        self.data[script] = data
    
    def __contains__(self, script):
        return script in self.data
    
api_key = "IDEY1N9XI1Y7HHUE"
script_data = ScriptData(api_key)

script = 'NVDA'
intraday_data = script_data.fetch_data(script)
intraday_data.get("Time Series (1min)")

if intraday_data is not None:
    time_series_data = intraday_data.get("Time Series (1min)")
    if time_series_data is not None:
        df_1 = pd.DataFrame.from_dict(time_series_data, orient='index')
        df_1 = df_1.astype({
            "1. open": float,
            "2. high": float,
            "3. low": float,
            "4. close": float,
            "5. volume": int
        })
        print(df_1)
    else:
        print(f"No intraday data found for {script}")
else:
    print(f"Failed to fetch intraday data for {script}")

df_1 = df_1.reset_index()
df_1.rename(columns = {'index':'timestamp'}, inplace = True)
df_1['timestamp'] = pd.to_datetime(df_1['timestamp'])

print(df_1)

def indicator1(df, timeperiod):
    df['indicator'] = df['4. close'].rolling(window = timeperiod, min_periods = 1). mean()
    return df[['timestamp', 'indicator', '4. close']]

timeperiod = 5
result = indicator1(df_1, timeperiod)

print(result)

class Strategy:
    def __init__(self, api_key):
        self.script_data = ScriptData(api_key)
        
    def generate_signals(self, script):
        # Fetch the historical data using the Script class
        df = self.script_data.fetch_data(script)
        if df is None:
            print(f"Failed to fetch intraday data for {script}")
            return None
        if df is not None:
            time_series_data = df.get("Time Series (1min)")
            if time_series_data is not None:
                df_2 = pd.DataFrame.from_dict(time_series_data, orient='index')
                df_2 = df_2.astype({
                    "1. open": float,
                    "2. high": float,
                    "3. low": float,
                    "4. close": float,
                    "5. volume": int
                })
            else:
                print(f"No intraday data found for {script}")
        else:
            print(f"Failed to fetch intraday data for {script}")

        df_2 = df_2.reset_index()
        df_2.rename(columns = {'index':'timestamp'}, inplace = True)
        df_2['timestamp'] = pd.to_datetime(df_2['timestamp'])
        
        timeperiod_1 = 5
        indicator_data = indicator1(df_2, timeperiod_1)
        
        signals = pd.DataFrame()
        signals['timestamp'] = df_2['timestamp']
        signals['close'] = df_2['4. close']
        signals['signal'] = 'No Signal'
        signals.loc[indicator_data['indicator']>df_2['4. close'], 'signal'] = 'Buy'
        signals.loc[indicator_data['indicator']<df_2['4. close'], 'signal'] = 'Sell'
        
        return signals
api_key = "IDEY1N9XI1Y7HHUE"
strategy = Strategy(api_key)

script = 'NVDA'
signals = strategy.generate_signals(script)
if signals is not None:
    
    print(signals.tail())

if signals is not None:
    ohlc = signals[['timestamp', 'close']].copy()
    ohlc.columns = ['Date', 'Close']
    ohlc['Open'] = ohlc['Close']
    ohlc['High'] = ohlc['Close']
    ohlc['Low'] = ohlc['Close']
    ohlc['Date'] = pd.to_datetime(ohlc['Date'])
    ohlc.set_index('Date', inplace=True)
    
    apds = [mpf.make_addplot(signals['signal'] == 'BUY', type='scatter', markersize=100, color='green'),
            mpf.make_addplot(signals['signal'] == 'SELL', type='scatter', markersize=100, color='red')]
    
    mpf.plot(ohlc, type='candle', addplot=apds, title=f'{script} Candlestick Chart with Signals')



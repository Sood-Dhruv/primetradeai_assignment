import pandas as pd

# Load the datasets (update paths to where you saved the files)
trader_df = pd.read_csv("historical_data.csv")
sentiment_df = pd.read_csv("fear_greed_index.csv")

# --- Inspect trader data ---
print("=== TRADER DATA ===")
print("Shape:", trader_df.shape)
print("\nColumns:", trader_df.columns.tolist())
print("\nFirst 3 rows:")
print(trader_df.head(3))
print("\nData types:")
print(trader_df.dtypes)

# --- Inspect sentiment data ---
print("\n=== FEAR/GREED DATA ===")
print("Shape:", sentiment_df.shape)
print("\nColumns:", sentiment_df.columns.tolist())
print("\nFirst 3 rows:")
print(sentiment_df.head(3))
print("\nUnique classifications:")
print(sentiment_df.iloc[:, 1].value_counts())



# --- Clean dates ---
trader_df['date'] = pd.to_datetime(trader_df['Timestamp IST'],format='mixed').dt.date.astype(str)
sentiment_df['date'] = pd.to_datetime(sentiment_df['date'],format='mixed').dt.date.astype(str)

# --- Fix sentiment classification ---
# The 'classification' column seems to have numbers, let's create proper labels
sentiment_df['sentiment_label'] = pd.cut(
    sentiment_df['value'],
    bins=[0, 24, 44, 55, 74, 100],
    labels=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
)

print("=== SENTIMENT LABEL DISTRIBUTION ===")
print(sentiment_df['sentiment_label'].value_counts())

# --- Merge ---
merged_df = trader_df.merge(sentiment_df[['date', 'value', 'sentiment_label']], on='date', how='inner')

print("\n=== MERGED DATA ===")
print("Shape:", merged_df.shape)
print("Date range covered:")
print("  From:", merged_df['date'].min())
print("  To:  ", merged_df['date'].max())
print("\nTrades per sentiment regime:")
print(merged_df['sentiment_label'].value_counts())
print("\nAny missing PnL values?", merged_df['Closed PnL'].isna().sum())





# --- PnL Analysis by Sentiment ---
print("=== PnL SUMMARY BY SENTIMENT REGIME ===\n")

pnl_summary = merged_df.groupby('sentiment_label').agg(
    Total_Trades      = ('Closed PnL', 'count'),
    Total_PnL         = ('Closed PnL', 'sum'),
    Avg_PnL_Per_Trade = ('Closed PnL', 'mean'),
    Median_PnL        = ('Closed PnL', 'median'),
    Win_Rate          = ('Closed PnL', lambda x: (x > 0).mean() * 100),
    Avg_Trade_Size    = ('Size USD',   'mean'),
).round(4)

# Order by sentiment severity
order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
pnl_summary = pnl_summary.reindex(order)

print(pnl_summary.to_string())

# --- Long vs Short breakdown ---
print("\n=== WIN RATE: LONG vs SHORT BY SENTIMENT ===\n")
ls_summary = merged_df.groupby(['sentiment_label', 'Side']).agg(
    Trades   = ('Closed PnL', 'count'),
    Win_Rate = ('Closed PnL', lambda x: (x > 0).mean() * 100),
    Avg_PnL  = ('Closed PnL', 'mean')
).round(3)

print(ls_summary.to_string())







# --- Leverage analysis ---
# First check if we have a leverage column, or derive it
print("=== LEVERAGE / POSITION SIZE ANALYSIS ===\n")

# Size USD as a proxy for risk appetite
size_by_sentiment = merged_df.groupby('sentiment_label').agg(
    Avg_Size_USD   = ('Size USD', 'mean'),
    Median_Size    = ('Size USD', 'median'),
    Total_Volume   = ('Size USD', 'sum'),
    Avg_Fee        = ('Fee', 'mean'),
).round(2).reindex(['Extreme Fear','Fear','Neutral','Greed','Extreme Greed'])

print(size_by_sentiment.to_string())

# --- Top traders vs bottom traders ---
print("\n=== TOP 10 vs BOTTOM 10 TRADERS (by total PnL) ===\n")
trader_pnl = merged_df.groupby('Account').agg(
    Total_PnL  = ('Closed PnL', 'sum'),
    Trades     = ('Closed PnL', 'count'),
    Win_Rate   = ('Closed PnL', lambda x: (x > 0).mean() * 100),
    Avg_PnL    = ('Closed PnL', 'mean'),
).round(2)

print("TOP 10:")
print(trader_pnl.nlargest(10, 'Total_PnL')[['Total_PnL','Trades','Win_Rate','Avg_PnL']].to_string())
print("\nBOTTOM 10:")
print(trader_pnl.nsmallest(10, 'Total_PnL')[['Total_PnL','Trades','Win_Rate','Avg_PnL']].to_string())







# --- Top & bottom trader accounts ---
top_accounts = trader_pnl.nlargest(10, 'Total_PnL').index.tolist()
bot_accounts = trader_pnl.nsmallest(10, 'Total_PnL').index.tolist()

merged_df['trader_tier'] = 'Mid'
merged_df.loc[merged_df['Account'].isin(top_accounts), 'trader_tier'] = 'Top'
merged_df.loc[merged_df['Account'].isin(bot_accounts), 'trader_tier'] = 'Bottom'

print("=== TOP TRADERS: behaviour by sentiment ===\n")
top_sentiment = merged_df[merged_df['trader_tier']=='Top'].groupby('sentiment_label').agg(
    Trades   = ('Closed PnL','count'),
    Win_Rate = ('Closed PnL', lambda x: (x>0).mean()*100),
    Avg_PnL  = ('Closed PnL','mean'),
    Avg_Size = ('Size USD','mean'),
).round(2).reindex(['Extreme Fear','Fear','Neutral','Greed','Extreme Greed'])
print(top_sentiment.to_string())

print("\n=== BOTTOM TRADERS: behaviour by sentiment ===\n")
bot_sentiment = merged_df[merged_df['trader_tier']=='Bottom'].groupby('sentiment_label').agg(
    Trades   = ('Closed PnL','count'),
    Win_Rate = ('Closed PnL', lambda x: (x>0).mean()*100),
    Avg_PnL  = ('Closed PnL','mean'),
    Avg_Size = ('Size USD','mean'),
).round(2).reindex(['Extreme Fear','Fear','Neutral','Greed','Extreme Greed'])
print(bot_sentiment.to_string())

print("\n=== CONTRARIAN SCORE: top traders ===")
print("(Buy during Fear/Extreme Fear, Sell during Greed/Extreme Greed)\n")
for tier, label in [('Top','TOP'), ('Bottom','BOTTOM')]:
    sub = merged_df[merged_df['trader_tier']==tier]
    fear_buys = len(sub[sub['sentiment_label'].isin(['Fear','Extreme Fear']) & (sub['Side']=='BUY')])
    greed_sells = len(sub[sub['sentiment_label'].isin(['Greed','Extreme Greed']) & (sub['Side']=='SELL')])
    total = len(sub)
    score = (fear_buys + greed_sells) / total * 100
    print(f"{label} traders contrarian score: {score:.1f}% of trades are contrarian")








    # --- Monthly PnL trend by sentiment ---
merged_df['month'] = pd.to_datetime(merged_df['date']).dt.to_period('M').astype(str)

monthly = merged_df.groupby(['month','sentiment_label']).agg(
    Total_PnL = ('Closed PnL','sum'),
    Trades    = ('Closed PnL','count')
).reset_index()

print("=== MONTHLY PnL TOTALS (first 10 rows) ===")
print(monthly.head(10).to_string())

# --- Most traded coins by sentiment ---
print("\n=== TOP 5 COINS TRADED PER SENTIMENT ===")
for s in ['Extreme Fear','Fear','Greed','Extreme Greed']:
    top_coins = merged_df[merged_df['sentiment_label']==s]['Coin'].value_counts().head(5)
    print(f"\n{s}:")
    print(top_coins.to_string())

# --- Fee drag analysis ---
print("\n=== TOTAL FEE DRAG BY SENTIMENT ===")
fee_drag = merged_df.groupby('sentiment_label').agg(
    Total_Fees = ('Fee','sum'),
    Total_PnL  = ('Closed PnL','sum'),
    Fee_to_PnL = ('Fee', lambda x: x.sum() / merged_df.loc[x.index,'Closed PnL'].sum() * 100)
).round(2).reindex(['Extreme Fear','Fear','Neutral','Greed','Extreme Greed'])
print(fee_drag.to_string())
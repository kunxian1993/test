from yf_scraper import stock_data

ticker = "QCOM"
df = stock_data.main(ticker)
df.sort_values(by=['endDate'], ascending=True, inplace=True)
print(df['endDate'])
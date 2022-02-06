import re
import json
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def extract_json(ticker):

    # set headers
    headers = { 
        'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
        'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
        'Accept-Language' : 'en-US,en;q=0.5',
        'DNT'             : '1', # Do Not Track Request Header 
        'Connection'      : 'close'
    }

    # html request
    stock_url = f"https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}"
    r = requests.get(stock_url, headers=headers, timeout=2)
    soup = BeautifulSoup(r.text, features="html.parser")

    # find javascript with all financial data
    pattern = re.compile(r"\s--\sData\s--\s")
    script_data = soup.find('script', text=pattern).contents[0]

    # extract json data
    start = script_data.find("context")-2
    json_data = json.loads(script_data[start:-12])
    
    return json_data

def extract_SummaryStore(SummaryStore_data):
    
    # extract data from json
    extracted = []
    for sheet in SummaryStore_data:
        statement={}
        for key, val in sheet.items():
            try:
                statement[key] = val["raw"]
            except TypeError:
                statement[key] = None
            except KeyError:
                statement[key] = None    

        extracted.append(statement)
    return extracted

def extract_fd(ticker, json_data):
    
    # extract financial data
    try:
        annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory']
        #quarterly_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistoryQuarterly']['incomeStatementHistory']

        #annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements']
        #quarterly_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistoryQuarterly']['cashflowStatements']

        #annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements']
        #quarterly_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistoryQuarterly']['balanceSheetStatements']    
    
    except KeyError:
        return
        
    fin_data = extract_SummaryStore(annual_is)
    df = pd.DataFrame(fin_data)
    df['Ticker'] = ticker
    df['endDate'] = df['endDate'].apply(lambda x:datetime.fromtimestamp(x))
    df['endDate'] = df['endDate'].dt.date
    
    return df

def extract_timeSeriesStore(ticker):
    
    json_data = extract_json(ticker)

    # extract data from json
    extracted = []
    try:
        json_data_keys = json_data['context']['dispatcher']['stores']['QuoteTimeSeriesStore']['timeSeries'].keys()
    except KeyError:
        return
    
    for key in json_data_keys:
        for row in json_data['context']['dispatcher']['stores']['QuoteTimeSeriesStore']['timeSeries'][key]:
            statement = {}        
            try:
                statement['Date'] = row['asOfDate']
                # remove "annual" or "trailing" at start of column name
                if key[:6] == 'annual':
                    statement[key[6:]] = row['reportedValue']['raw']
                else:
                    statement[key[8:]] = row['reportedValue']['raw']             
                extracted.append(statement)

            except TypeError:
                pass
            except KeyError:
                pass
    
    df = pd.DataFrame(extracted)
    df = df.groupby(['Date']).sum()
    df.reset_index(inplace=True)
    df['Ticker'] = ticker
    
    return df

def main(ticker):
    json_data = extract_json(ticker)
    return extract_fd(ticker, json_data)
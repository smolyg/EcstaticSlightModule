from types import EllipsisType
from flask import Flask
from datetime import datetime, timedelta
from datetime import date
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import json

app = Flask(__name__)


#returns DF or JSON with options strikes near price within depth provided for number of days out
def put_recommendation(security, price, depth, max_days_out):
  today = date.today()
  all_puts = pd.DataFrame()
  exps = security.options  #get the full list of expiration dates
  for e in exps:
    exp_date = datetime.strptime(e, "%Y-%m-%d")
    one_month_later = today + timedelta(days=30)  #month later
    months_later = today + timedelta(days=max_days_out)  #max days out
    if one_month_later < exp_date.date() < months_later:
      opt = security.option_chain(e)
      puts_chain = opt.puts
      puts_chain['Expiration'] = e
      all_puts = pd.concat([all_puts, puts_chain], ignore_index=True)

  all_puts = all_puts.query('strike < @price')
  all_puts['Profit'] = round(
      ((all_puts['bid'] + all_puts['ask']) / 2) / all_puts['strike'] * 100, 2)
  return all_puts.to_html()


def opt_chain(ticker):
  stock = yf.Ticker(ticker)
  price = (float(stock.info["bid"]) + float(stock.info["ask"])) / 2
  return put_recommendation(stock, price, 20, 90)

  #return stock.info['longBusinessSummary']


@app.route('/')
def index():
  #return opt_chain("TAN")
  return 'please use followin URL: /stock/ticker'


#examle to call this function /stock/SOXL
@app.route('/stock/<ticker>')
def stock(ticker):
  if ticker == "":
    return "please use followin URL: /stock/ticker"
  else:
    return opt_chain(ticker)


app.run(host='0.0.0.0', port=81)

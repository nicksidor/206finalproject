# SI 206 Final Project
# Cryptocurrency Project
# Ari Feldberg, Alaa Shahin, Nick Sidor

from pycoingecko import CoinGeckoAPI
import datetime
import time
import sqlite3
import os
from pytrends.request import TrendReq
from pytrends import dailydata

pytrends = TrendReq(hl='en-US', tz=360)

cg = CoinGeckoAPI()


# returns the last 100 days of Google Trends values for Dogecoin
def getDogecoinTrends():
    kw_list = "dogecoin"
    info = dailydata.get_daily_data(kw_list, 2021, 1, 2021, 4)
    info.reset_index(inplace=True)

    info['date'] = info['date'].astype(str)
    subset = info[["date", "dogecoin_unscaled"]]

    tuples = [tuple(x) for x in subset.to_numpy()]
    tuples = tuples[-100:]

    return tuples


# returns the last 25 days of doge price (in USD) that were not already added to the table from coingecko
def getPrevDOGE(cur, conn):
    cur.execute('SELECT date FROM DogeDateIDs')
    results = cur.fetchall()

    date_list = []
    for i in results:
        date_list.append(i[0])
    date_list = date_list[-25:]

    prevPrices = []
    for i in range(0, len(date_list)):
        date = date_list[i]
        format_str = '%Y-%m-%d'
        datetime_obj = datetime.datetime.strptime(date, format_str)
        date = str(datetime_obj.strftime('%d-%m-%Y')) + " 00:00:00"

        history = cg.get_coin_history_by_id(id='dogecoin', date=date, vs_currencies='usd', localization='false')

        price = history['market_data']['current_price']['usd']
        price = str(round(price, 5))

        prevPrices.append((price, date))

        time.sleep(0.3)

    return prevPrices


# adds Google Trends values to tables and also adds dates to a separate table, with both having the same id/key
def addTrendsToTable(cur, conn):
    trendsData = getDogecoinTrends()
    cur.execute('SELECT id FROM DogecoinTrends')
    trend_list = cur.fetchall()

    x = 1
    count = len(trend_list)

    for x in range(25):
        x = count

        cur.execute("INSERT OR IGNORE INTO DogecoinTrends (id, trend_value) VALUES (?, ?)", (count, trendsData[x][1]))
        cur.execute("INSERT OR IGNORE INTO DogeDateIDs (id, date) VALUES (?, ?)", (count, trendsData[x][0]))
        count += 1

    conn.commit()


# adds dogecoin price to DogecoinUSDPast table 25 prices at a time
def addPriceToTable(cur, conn):
    priceData = getPrevDOGE(cur, conn)
    cur.execute('SELECT id FROM DogecoinUSDPast')
    price_list = cur.fetchall()

    count = len(price_list)

    for i in range(25):
        cur.execute("INSERT OR IGNORE INTO DogecoinUSDPast (id, usd_price) VALUES (?, ?)", (count, priceData[i][0]))
        count += 1

    conn.commit()


# sets up three tables within crypto.db
def setUpTables(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS DogecoinUSDPast (id INTEGER PRIMARY KEY, usd_price INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS DogecoinTrends (id INTEGER PRIMARY KEY, trend_value INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS DogeDateIDs (id INTEGER PRIMARY KEY, date TEXT)")
    conn.commit()


# main executes the necessary functions to properly run doge.py
def main():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/crypto.db')
    cur = conn.cursor()

    setUpTables(cur, conn)

    addTrendsToTable(cur, conn)

    addPriceToTable(cur, conn)


if __name__ == "__main__":
    main()

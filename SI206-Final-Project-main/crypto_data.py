# SI 206 Final Project
# Cryptocurrency Project
# Ari Feldberg, Alaa Shahin, Nick Sidor

from pycoingecko import CoinGeckoAPI
import sqlite3
import requests
import os

cg = CoinGeckoAPI()


# calculates average change in price of the top 100 cryptocurrencies (in market cap values) over the last 24 hours
def getAvgChange(cur, conn):
    cur.execute("SELECT perc_price_change FROM Top100Coins")
    outputLst = cur.fetchall()

    percChange = []
    for tup in outputLst:
        percChange.append(tup[0])

    avg = sum(percChange) / len(percChange)

    return avg


# gets top 100 cryptocurrencies and returns a list of important data about each coin
def getTop100Coins():
    coins = []
    r = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc")
    content = r.json()

    for coin in content:
        coins.append([coin['market_cap_rank'], coin['id'], coin['current_price'],
                      coin['market_cap'], coin['price_change_percentage_24h']])

    return coins


# adds the top 100 coins to two tables within crypto.db
def addTopCoins(cur, conn):
    top100Coins = getTop100Coins()
    cur.execute('SELECT coin_rank FROM Top100Coins')
    coin_list = cur.fetchall()

    x = 1
    count = len(coin_list)

    for x in range(25):
        x = count
        rank = top100Coins[x][0]

        name = top100Coins[x][1]
        price = top100Coins[x][2]
        mkt_cap = top100Coins[x][3]
        change = top100Coins[x][4]
        cur.execute("INSERT OR IGNORE INTO Top100Coins (coin_rank, curr_usd_price, curr_usd_mkt_cap, "
                    "perc_price_change) VALUES (?, ?, ?, ?)", (rank, price, mkt_cap, change))
        cur.execute("INSERT OR IGNORE INTO Top100CoinsIDs (coin_rank, coin_name) VALUES (?, ?)", (rank, name))
        count += 1

    conn.commit()


# creates the database crypto.db
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn


# sets up two tables within crypto.db
def setUpTables(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Top100Coins (coin_rank INTEGER PRIMARY KEY, "
                "curr_usd_price INTEGER, curr_usd_mkt_cap INTEGER, perc_price_change INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS Top100CoinsIDs (coin_rank INTEGER PRIMARY KEY, coin_name TEXT)")
    conn.commit()


# writes data calculated within this file to a txt file (cryptodata.txt)
def write_data_to_file(filename, cur, conn):
    cur.execute('SELECT coin_rank FROM Top100Coins')
    coin_list = cur.fetchall()

    if len(coin_list) == 100:
        path = os.path.dirname(os.path.abspath(__file__)) + os.sep

        outFile = open(path + filename, "w")
        outFile.write("Average % Price Change of the Top 100 Cryptocurrencies\n")
        outFile.write("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■\n\n")
        avgCryptoChange = (getAvgChange(cur, conn))
        # This line rounds the average popularity to one decimal place.
        avgCrypto = round(avgCryptoChange, 4)
        outFile.write("The average percent change of the price of the top 100\n            cryptocurrencies is "
                      + str(avgCrypto) + "%." + "\n\n\n")

        top100Coins = getTop100Coins()
        top10Coins = []
        for i in range(10):
            top10Coins.append((top100Coins[i][1], top100Coins[i][3], top100Coins[i][2]))

        outFile.write("        Top 5 Cryptocurrency Market Caps (USD)        \n")
        outFile.write("-====================================================-\n\n")
        for i in range(5):
            outFile.write("#{}: {} (${})\n".format(i + 1, top10Coins[i][0], top10Coins[i][1]))
        outFile.write("\n\n")

        outFile.write("        Top 10 Cryptocurrency Coin Prices (USD)       \n")
        outFile.write("-====================================================-\n\n")
        for i in range(10):
            outFile.write("#{}: {} (${})\n".format(i + 1, top10Coins[i][0], top10Coins[i][2]))

        outFile.close()


# main executes the necessary functions to properly run crypto_data.py
def main():
    cur, conn = setUpDatabase('crypto.db')

    setUpTables(cur, conn)

    addTopCoins(cur, conn)

    write_data_to_file("cryptodata.txt", cur, conn)


if __name__ == "__main__":
    main()

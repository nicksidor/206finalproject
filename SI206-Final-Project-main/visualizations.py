# SI 206 Final Project
# Cryptocurrency Project
# Ari Feldberg, Alaa Shahin, Nick Sidor

import sqlite3
import os
import dateutil
import numpy as np
import matplotlib.pyplot as plt
import mplcursors


# returns tuple of market caps and coin names through table joins
def joinTablesTwitter(cur, conn):
    cur.execute(
        "SELECT Top100CoinsIDs.coin_name, Top100Coins.curr_usd_mkt_cap FROM Top100Coins LEFT JOIN Top100CoinsIDs ON "
        "Top100Coins.coin_rank = Top100CoinsIDs.coin_rank")
    results = cur.fetchall()
    conn.commit()

    return results


# returns tuple of percent price change and coin names through table joins
def joinTablesCrypto(cur, conn):
    cur.execute(
        "SELECT Top100Coins.perc_price_change, Top100CoinsIDs.coin_name FROM Top100Coins LEFT JOIN Top100CoinsIDs ON "
        "Top100Coins.coin_rank = Top100CoinsIDs.coin_rank")
    results = cur.fetchall()
    conn.commit()

    return results


# returns tuple of dates and past prices through table joins
def joinTablesDogePrice(cur, conn):
    cur.execute("SELECT DogeDateIDs.date, DogecoinUSDPast.usd_price FROM DogeDateIDs LEFT JOIN DogecoinUSDPast ON "
                "DogeDateIDs.id = DogecoinUSDPast.id")
    results = cur.fetchall()
    conn.commit()

    return results


# returns tuple of dates and trend values through table joins
def joinTablesTrends(cur, conn):
    cur.execute("SELECT DogeDateIDs.date, DogecoinTrends.trend_value FROM DogeDateIDs LEFT JOIN DogecoinTrends ON "
                "DogeDateIDs.id = DogecoinTrends.id")
    results = cur.fetchall()
    conn.commit()

    return results


# calculates average change in price of the top 100 cryptocurrencies (in market cap values) over the last 24 hours
def getAvgChange(cur, conn):
    cur.execute("SELECT perc_price_change FROM Top100Coins")
    outputLst = cur.fetchall()

    percChange = []
    for tup in outputLst:
        percChange.append(tup[0])

    avg = sum(percChange) / len(percChange)

    return avg


# makes bar graph of the percent change of the top 10 cryptocurrencies (market cap values), along with an average line
def makeCryptoBar(cur, conn):
    avgCrypto = getAvgChange(cur, conn)
    ind = np.arange(10)
    width = 0.4

    outputLst = joinTablesCrypto(cur, conn)

    percChange = []
    coinNames = []
    for i in range(10):
        percChange.append(outputLst[i][0])
        coinNames.append(outputLst[i][1])
    percChange = tuple(percChange)
    coinNames = tuple(coinNames)

    fig, ax = plt.subplots()
    p1 = ax.bar(ind, percChange, width, label='Coins')

    x1 = [-1, 10]
    y1 = [avgCrypto, avgCrypto]
    avgCrypto = round(avgCrypto, 4)
    plt.plot(x1, y1, label="Average 24h Change\nof Top 100 Coins\n({}%)".format(avgCrypto), color='red')

    ax.axhline(0, color='grey', linewidth=0.8)
    ax.set_ylabel('Percent Change in Last 24 Hours')
    ax.set_title('Percent Change in Last 24 Hours of the top 10 Cryptocurrencies')
    ax.set_xticks(ind)
    ax.set_xticklabels(coinNames)
    ax.legend()
    mplcursors.cursor(hover=True)

    plt.show()


# makes two stacked bar graphs comparing the top coin market caps and the top coin twitter account follower counts,
# showing a correlation between coin market cap and twitter popularity
def makeTwitterBar(cur, conn):
    ind = np.arange(10)
    ind2 = np.arange(10)
    width = 0.4

    cur.execute("SELECT coin_name, twitter_followers FROM Top100CoinsFollowers")
    outputLst = cur.fetchall()
    coinNames = []
    twitterFollowers = []
    for i in range(10):
        coinNames.append(outputLst[i][0])
        twitterFollowers.append(outputLst[i][1])
    twitterFollowers = tuple(twitterFollowers)
    coinNamesTwitter = tuple(coinNames)

    topMktCap = joinTablesTwitter(cur, conn)
    coinNames2 = []
    topMktCapLst = []
    for i in range(10):
        coinNames2.append(topMktCap[i][0])
        topMktCapLst.append(topMktCap[i][1])
    topMktCapLst = tuple(topMktCapLst)
    coinNamesMktCap = tuple(coinNames2)

    fig, (ax1, ax2) = plt.subplots(2)
    fig.suptitle('Top 10 Coins in Twitter Followers and Market Caps (in USD)')
    p1 = ax1.bar(ind, twitterFollowers, width, label='Coins')
    p2 = ax2.bar(ind2, topMktCapLst, width, label='test')

    ax1.axhline(0, color='grey', linewidth=0.8)
    ax1.set_ylabel('Number of Followers on Twitter')
    ax1.set_title('Top 10 Most Followed Crpytocurrency Twitter Accounts')
    ax1.set_xticks(ind)
    ax1.set_xticklabels(coinNamesTwitter)

    ax2.axhline(0, color='grey', linewidth=0.8)
    ax2.set_ylabel('Market Cap (in USD)')
    ax2.set_title('Market Cap (in USD) of the top 10 Cryptocurrencies')
    ax2.set_xticks(ind)
    ax2.set_xticklabels(coinNamesMktCap)

    plt.subplots_adjust(hspace=0.5)
    mplcursors.cursor(hover=True)

    plt.show()


# makes two trend lines comparing dogecoin price (in USD) and its google trend value, showing a correlation between
# coin price and search activity
def dogeTrendline(cur, conn):
    priceData = joinTablesDogePrice(cur, conn)
    priceDates = []
    prices = []
    for i in priceData:
        priceDates.append(i[0])
        prices.append(i[1])

    trendData = joinTablesTrends(cur, conn)
    trends = []
    for i in trendData:
        trends.append(i[1])

    dates = [dateutil.parser.parse(x) for x in priceDates]

    fig, (ax1, ax2) = plt.subplots(2)

    ax1.plot(dates, prices)
    ax1.set_title("Dogecoin Price (in USD) Over the Last 100 Days")
    ax1.set_ylabel('Price (in USD)')
    ax1.set_xlabel("Dates (YYYY-MM-DD)")

    ax2.plot(dates, trends)
    ax2.set_title("Dogecoin Google Trends Data Over the Last 100 Days")
    ax2.set_ylabel("Google Trends Value")
    ax2.set_xlabel("Dates (YYYY-MM-DD)")

    plt.subplots_adjust(hspace=0.6)
    mplcursors.cursor(hover=True)

    plt.show()


# main executes the necessary functions to properly run visualizations.py
def main():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/crypto.db')
    cur = conn.cursor()

    makeCryptoBar(cur, conn)

    makeTwitterBar(cur, conn)

    dogeTrendline(cur, conn)


if __name__ == "__main__":
    main()

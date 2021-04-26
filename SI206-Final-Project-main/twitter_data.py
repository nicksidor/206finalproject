# SI 206 Final Project
# Cryptocurrency Project
# Ari Feldberg, Alaa Shahin, Nick Sidor

import sqlite3
import tweepy
import os
import time

consumer_key = "GM2osUTm9qKJlnJtr14hb4CfJ"
consumer_secret = "RDm73ejW2h0vSmkBTGx4lZGoSXJmq9olO2OS5JGyAyN9COKUIq"
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit=True)


# joins Top100CoinsIDs and Top100Coins to return the names of coins with their ids
def joinTables(cur, conn):
    cur.execute(
        "SELECT Top100CoinsIDs.coin_name FROM Top100Coins LEFT JOIN Top100CoinsIDs ON "
        "Top100Coins.coin_rank = Top100CoinsIDs.coin_rank")
    results = cur.fetchall()
    conn.commit()
    names = []
    for i in results:
        names.append(i[0])

    return names


# will try to read in from a file containing follower count data
# if unable to read from file (does not exist yet/first time running file), it will get the proper follower count data,
# create a list with it, and create/write it to a file. doing this helps speed up run time because getting data from
# tweepy takes a while, so storing it in a cache file helps speed up the process.
def getSortedFollowerCounts(topCoins):
    try:
        followerCounts = []
        with open("followerdata.txt", "r") as file:
            for i in file.readlines():
                tmp = i.split(",")
                try:
                    followerCounts.append((int(tmp[0]), tmp[1].rstrip()))
                except:
                    pass

    except:
        followerCounts = []

        percent = 0
        for x in topCoins:
            try:
                x = x.replace('-', '')
                user = api.get_user(x)
                followerCounts.append((user['followers_count'], x))
                time.sleep(0.5)
            except:
                followerCounts.append((0, x + " (N/A)"))
            print("{}% done".format(percent))
            percent += 1

        print("Done!")

        followerCounts = sorted(followerCounts, reverse=True)

        file = open("followerdata.txt", "w+")

        for i in followerCounts:
            file.write(','.join(str(s) for s in i) + '\n')

        file.close()

    return followerCounts


# adds the necessary information to the table
def addToTable(cur, conn):
    topCoins = joinTables(cur, conn)
    followerCounts = getSortedFollowerCounts(topCoins)
    cur.execute('SELECT followers_rank FROM Top100CoinsFollowers')
    coin_list = cur.fetchall()

    count = len(coin_list)

    for x in range(25):
        x = count

        cur.execute("INSERT OR IGNORE INTO Top100CoinsFollowers (followers_rank, coin_name, twitter_followers) "
                    "VALUES (?, ?, ?)", (count + 1, followerCounts[x][1], followerCounts[x][0]))
        count += 1

    conn.commit()


# sets up one table within crypto.db
def setUpTables(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Top100CoinsFollowers (followers_rank INTEGER PRIMARY KEY, coin_name TEXT, "
                "twitter_followers INTEGER)")
    conn.commit()


# main executes the necessary functions to properly run twitter_data.py
def main():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/crypto.db')
    cur = conn.cursor()

    setUpTables(cur, conn)

    addToTable(cur, conn)


if __name__ == "__main__":
    main()

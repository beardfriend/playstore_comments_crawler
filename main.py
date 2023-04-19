from crawler import Crawler
from db import connect, insertQueryApps
from tqdm import tqdm
from print import printWithFence


def main():
    ## init global variables
    appInfo = None
    reqReviewCount = 0

    # initDatabase
    db = connect()

    # init Cralwer
    playStoreCrawler = Crawler(db)

    # prompter ( App Check )
    processStart = False
    while processStart == False:
        reqAppName = input("Please enter app name to crawl: ")

        appInfo = playStoreCrawler.searchAppByName(reqAppName)
        printWithFence(appInfo["name"])

        yesOrNo = input("Is that the app name you were looking for? ? (y | n): ")

        if yesOrNo == "y":
            processStart = True
        else:
            printWithFence("try again...")

    # prompter ( How many reviews do you want to extract? )
    printWithFence(
        "total reivews :", playStoreCrawler.crawlReviewCount(appInfo["appStoreId"])
    )
    reqReviewCount = int(
        input("Please enter the number of comments to crawl (as a number): ")
    )

    # printing (start crawling)
    printWithFence("Start the crawl.")

    # insert request information into database
    cursor = db.cursor()
    cursor.execute(
        insertQueryApps, (appInfo["name"], reqReviewCount, appInfo["appStoreId"])
    )
    lastId = cursor.lastrowid
    db.commit()
    cursor.close()

    # start crawling
    ## init progress bar
    pbar = tqdm(total=reqReviewCount)
    ## start crawl
    playStoreCrawler.crawlComments(appInfo["appStoreId"], lastId, pbar)
    ## close progress bar
    pbar.close()

    # finish
    print("finish :) ")
    print("your database id: " + str(lastId))


main()

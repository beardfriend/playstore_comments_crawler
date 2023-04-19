from crawler import Crawler
from db import connect, insertQueryApps
from tqdm import tqdm


def main():
    db = connect()
    playStoreCrawler = Crawler(db)
    appName = input("크롤링할 앱 이름을 입력해주세요 : ")
    result = playStoreCrawler.getInfoByname(appName)

    print("------------------------")
    print(result["name"])
    print("------------------------")

    isContinue = input("크롤링할 앱이 맞나요? (y | n): ")

    if isContinue == "y":
        print("------------------------")
        print("리뷰 총 개수: ", playStoreCrawler.crawlReviewCount(result["appId"]))
        print("------------------------")
        howmany = int(input("크롤링할 댓글 개수를 입력해주세요(숫자로) : "))
        print("크롤링을 시작합니다 :) ")
        print("\n")

        # insert app info
        cursor = db.cursor()
        cursor.execute(insertQueryApps, (result["name"], howmany, result["appId"]))
        lastid = cursor.lastrowid
        db.commit()
        cursor.close()

        pbar = tqdm(total=howmany)

        playStoreCrawler.crawlComments(
            appId=result["appId"],
            appRowId=lastid,
            progressBar=pbar,
            howmany=howmany,
        )

        pbar.close()
    else:
        print("재실행 해주세요 !! :) ")
        quit()

    print("모두 수집되었습니다. :) ")
    print('수집한 데이터에 접근하시려면 숫자 : "' + str(lastid) + '"를 기억해주세요')


main()

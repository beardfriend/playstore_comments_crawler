from crawler import Crawler
from tqdm import tqdm


def main():
    playStoreCrawler = Crawler()
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
        pbar = tqdm(total=howmany)
        playStoreCrawler.crawlComments(
            result["appId"],
            progressBar=pbar,
            howmany=howmany,
        )
        pbar.close()
    else:
        print("재실행 해주세요 !! :) ")
        quit()

    print("모두 수집되었습니다. :) ")


main()

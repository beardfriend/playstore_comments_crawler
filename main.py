from crawler import Crawler


def main():
    playStoreCrawler = Crawler()
    appName = input("크롤링할 앱 이름을 입력해주세요 : ")
    result = playStoreCrawler.getInfoByname(appName)

    print("------------------------")
    print(result["name"])
    print("------------------------")

    isContinue = input("크롤링할 앱이 맞나요? (y | n): ")

    if isContinue == "y":
        playStoreCrawler.crawlComments(result["appId"])
    else:
        print("재실행 해주세요 !! :) ")
        quit()


main()

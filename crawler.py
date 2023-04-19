from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import re


class Crawler:
    def __init__(self):
        self.playStore = {
            "listPage": {
                "defaultUrl": "https://play.google.com/store/search?q=",
                "query": "",
                "basicQuery": "&c=apps&hl=ko",
            },
            "detailPage": {
                "defaultUrl": "https://play.google.com/store/apps/details?id=",
                "query": "",
                "basicQuery": "&hl=ko",
            },
        }

        self.soup = None
        self.driver = None

    def getInfoByname(self, name):
        pageInfo = self.playStore["listPage"]
        url = pageInfo["defaultUrl"] + quote(name) + pageInfo["basicQuery"]

        response = requests.get(url)
        self.soup = BeautifulSoup(response.content, "html.parser")

        container = self.soup.find("div", {"class": "XUIuZ"})

        if container == None:
            appId, title, madeBy = self._inCorrectQuery()
        else:
            appId, title, madeBy = self._correctQuery(container)

        self._resetSoup()

        return {"name": title.text + " madeBy " + madeBy.text, "appId": appId}

    def _correctQuery(self, container):
        appId = container.find("a", {"class": "Qfxief"}).attrs["href"].split("?id=")[1]
        title = container.find("div", {"class": "vWM94c"})
        madeBy = container.find("div", {"class": "LbQbAe"})
        return (
            appId,
            title,
            madeBy,
        )

    def _inCorrectQuery(self):
        # get app Id
        link = self.soup.find("a", {"class": "Si6A0c"})
        appId = link.attrs["href"].split("?id=")[1]

        # get default information
        information = self.soup.find("div", {"class": "cXFu1"})

        title = information.find("span", {"class": "DdYX5"})
        madeBy = information.find("span", {"class": "wMUdtb"})
        return (
            appId,
            title,
            madeBy,
        )

    def _resetSoup(self):
        self.soup = None

    def crawlComments(
        self,
        appId,
        startDate="1",
        endDate="2",
        minStarredCount="1",
        maxStarredCount="5",
        howmany=200,
    ):
        pageInfo = self.playStore["detailPage"]
        url = pageInfo["defaultUrl"] + appId + pageInfo["basicQuery"]

        self._setSelenium()
        self.driver.get(url)

        # click
        button = self.driver.find_element(
            By.XPATH,
            '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div[2]/div/div[1]/c-wiz[4]/section/header/div/div[2]/button/i',
        )

        ActionChains(self.driver).move_to_element(button).pause(1).click().pause(
            1
        ).perform()

        time.sleep(2)
        commentEles = self.driver.find_element(
            By.XPATH,
            '//*[@id="yDmH0d"]/div[4]/div[2]/div/div/div/div/div[2]',
        )

        # 첫 번째 방법 요소 길이를 구하고
        # 요소 길이를 구하고 길이가 다 되면 스크롤해서 길이부터 계속 크롤링
        collectedCount = 0

        parent = commentEles.find_element(By.XPATH, "./div/div[1]")

        while collectedCount < howmany:
            length = len(parent.find_elements(By.XPATH, "./*"))
            for i in range(collectedCount, length):
                element = parent.find_element(By.XPATH, f"./div[{i+1}]")

                # 유저이름
                userName = element.find_element(
                    By.XPATH, "./header/div[1]/div[1]/div"
                ).text

                # 별점
                starred = element.find_element(
                    By.XPATH, "./header/div[2]/div"
                ).get_attribute("aria-label")

                # 리뷰시점
                reviewedAt = element.find_element(By.XPATH, "./header/div[2]/span").text

                # 리뷰 내용
                content = element.find_element(By.XPATH, "./div[1]").text

                # 유용하다고 평가한 사람의 수
                usefulCount = 0
                try:
                    usefulCount = re.sub(
                        r"[^0-9]",
                        "",
                        element.find_element(By.XPATH, "./div[2]/div").text,
                    )
                except:
                    continue

                print(usefulCount)

            collectedCount = length

            self._scrollDown(commentEles)

    def _scrollDown(self, parent):
        scroll_origin = ScrollOrigin.from_element(parent)
        ActionChains(self.driver).scroll_from_origin(scroll_origin, 0, 10000).perform()

    def _setSelenium(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome("./chromedriver", options=options)

    # def _savePoint():

    # def checkprogressed():

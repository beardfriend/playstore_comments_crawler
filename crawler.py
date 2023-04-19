from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from db import insertQueryComments
import re
from tqdm import tqdm
from datetime import datetime


class Crawler:
    def __init__(self, db):
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
        self.database = db

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

    def crawlReviewCount(self, appId):
        pageInfo = self.playStore["detailPage"]
        url = pageInfo["defaultUrl"] + appId + pageInfo["basicQuery"]

        response = requests.get(url)
        self.soup = BeautifulSoup(response.content, "html.parser")

        container = self.soup.find("div", {"class": "g1rdde"})

        reviewCount = container.text.split(" ")[1]
        self._resetSoup()

        return reviewCount

    def crawlComments(
        self,
        appId,
        appRowId,
        progressBar,
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
        commentEles = None
        try:
            commentEles = self.driver.find_element(
                By.XPATH,
                '//*[@id="yDmH0d"]/div[4]/div[2]/div/div/div/div/div[2]',
            )
        except:
            commentEles = self.driver.find_element(
                By.XPATH,
                '//*[@id="yDmH0d"]/div[3]/div[2]/div/div/div/div/div[2]',
            )

        collectedCount = 0
        parent = commentEles.find_element(By.XPATH, "./div/div[1]")

        while collectedCount < howmany:
            length = len(parent.find_elements(By.XPATH, "./*"))

            for i in range(collectedCount, length):
                if collectedCount == howmany:
                    break

                element = parent.find_element(By.XPATH, f"./div[{i+1}]")

                # 유저이름
                userName = element.find_element(
                    By.XPATH, "./header/div[1]/div[1]/div"
                ).text

                # 별점
                s = element.find_element(By.XPATH, "./header/div[2]/div").get_attribute(
                    "aria-label"
                )

                rating = float(
                    element.find_element(By.XPATH, "./header/div[2]/div")
                    .get_attribute("aria-label")
                    .split(" ")[3][:1]
                )

                # 리뷰시점
                reviewedAt = element.find_element(By.XPATH, "./header/div[2]/span").text

                date_obj = datetime.strptime(reviewedAt, "%Y년 %m월 %d일")

                reviewdAtDate = date_obj.strftime("%Y-%m-%d")
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
                    usefulCount = 0
                # insert into database
                cursor = self.database.cursor()
                cursor.execute(
                    insertQueryComments,
                    (appRowId, userName, rating, reviewdAtDate, content, usefulCount),
                )
                self.database.commit()
                cursor.close()
                progressBar.update(1)
                collectedCount += 1
            self._scrollDown(commentEles)

    def _scrollDown(self, parent):
        scroll_origin = ScrollOrigin.from_element(parent)
        ActionChains(self.driver).scroll_from_origin(scroll_origin, 0, 10000).perform()

    def _setSelenium(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome("./chromedriver", options=options)

    # def _savePoint():

    # def checkprogressed():

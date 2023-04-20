from bs4 import BeautifulSoup
import requests

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from db import insertQueryReviews
import re
from urllib.parse import urlencode
from datetime import datetime


class Crawler:
    def __init__(self, db):
        self.playStore = {
            "listPage": {
                "url": "https://play.google.com/store/search",
                "query": {"c": "apps", "hl": "ko"},  # q
            },
            "detailPage": {
                "url": "https://play.google.com/store/apps/details",
                "query": {"hl": "ko"},  # id
            },
        }

        self.soup = None
        self.driver = None
        self.database = db

    def searchAppByName(self, name):
        # set url
        self._addQuery("listPage", {"q": name})
        url = self._getUrl("listPage")
        print(url)
        # get html
        response = requests.get(url)

        self.soup = BeautifulSoup(response.content, "html.parser")
        container = self.soup.find("div", {"class": "XUIuZ"})

        # extract
        if container == None:
            appStoreId, title, madeBy = self._recommandPage()
        else:
            appStoreId, title, madeBy = self._normalPage(container)

        # reset
        self._resetSoup()
        self._resetQuery()

        return {"name": title.text + " madeBy " + madeBy.text, "appStoreId": appStoreId}

    def _getUrl(self, key):
        queryString = urlencode(self.playStore[key]["query"])
        return f'{self.playStore[key]["url"]}?{queryString}'

    def _addQuery(self, key, query):
        self.playStore[key]["query"].update(query)

    def _resetQuery(self):
        self.playStore["listPage"]["query"] = {"c": "apps", "hl": "ko"}
        self.playStore["detailPage"]["query"] = {"hl": "ko"}

    def _normalPage(self, container):
        appId = container.find("a", {"class": "Qfxief"}).attrs["href"].split("?id=")[1]
        title = container.find("div", {"class": "vWM94c"})
        madeBy = container.find("div", {"class": "LbQbAe"})
        return (
            appId,
            title,
            madeBy,
        )

    def _recommandPage(self):
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

    def crawlReviewCount(self, appStoreId):
        # set url
        self._addQuery("detailPage", {"id": appStoreId})
        url = self._getUrl("detailPage")

        # get html
        response = requests.get(url)
        self.soup = BeautifulSoup(response.content, "html.parser")
        container = self.soup.find("div", {"class": "g1rdde"})

        # reset
        self._resetSoup()
        self._resetQuery()

        # transform
        reviewCount = container.text.split(" ")[1]

        return reviewCount

    def crawlReviews(
        self,
        appStoreId,
        appRowId,
        progressBar,
        reqReviewCount=200,
    ):
        # set url
        self._addQuery("detailPage", {"id": appStoreId})
        url = self._getUrl("detailPage")

        # start chrome browser with headless
        self._setSelenium()
        self.driver.get(url)

        # click more reviews
        button = self.driver.find_element(
            By.XPATH,
            '//*[@id="yDmH0d"]/c-wiz[2]/div/div/div[1]/div[2]/div/div[1]/c-wiz[4]/section/header/div/div[2]/button/i',
        )
        ActionChains(self.driver).move_to_element(button).pause(1).click().pause(
            1
        ).perform()
        time.sleep(2)

        # finding reviewsContainer
        reviewsPopup = None
        try:
            reviewsPopup = self.driver.find_element(
                By.XPATH,
                '//*[@id="yDmH0d"]/div[4]/div[2]/div/div/div/div/div[2]',
            )
        except:
            reviewsPopup = self.driver.find_element(
                By.XPATH,
                '//*[@id="yDmH0d"]/div[3]/div[2]/div/div/div/div/div[2]',
            )
        reviewsContainer = reviewsPopup.find_element(By.XPATH, "./div/div[1]")

        # crawl comment
        collectedCount = 0
        while collectedCount < reqReviewCount:
            renderedreviews = len(reviewsContainer.find_elements(By.XPATH, "./*"))
            for i in range(collectedCount, renderedreviews):
                # stop
                if collectedCount == reqReviewCount:
                    break

                comment = reviewsContainer.find_element(By.XPATH, f"./div[{i+1}]")

                # crawl Review Info
                (
                    userName,
                    rating,
                    reviewdAt,
                    content,
                    usefulCount,
                ) = self._crawlReviewInfo(comment)

                # insert into database
                cursor = self.database.cursor()
                cursor.execute(
                    insertQueryReviews,
                    (appRowId, userName, rating, reviewdAt, content, usefulCount),
                )
                self.database.commit()
                cursor.close()

                # update Progress Bar
                progressBar.update(1)

                # update collected Count
                collectedCount += 1

            # rendering review
            self._scrollDown(reviewsContainer)
        self._resetQuery()

    def _scrollDown(self, parent):
        scroll_origin = ScrollOrigin.from_element(parent)
        ActionChains(self.driver).scroll_from_origin(scroll_origin, 0, 10000).perform()

    def _setSelenium(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome("./chromedriver", options=options)

    def _crawlReviewInfo(self, comment):
        # get userName
        userName = comment.find_element(By.XPATH, "./header/div[1]/div[1]/div").text
        # get rating
        rating = float(
            comment.find_element(By.XPATH, "./header/div[2]/div")
            .get_attribute("aria-label")
            .split(" ")[3][:1]
        )
        # get reviewdAt
        reviewedAtRaw = comment.find_element(By.XPATH, "./header/div[2]/span").text
        date_obj = datetime.strptime(reviewedAtRaw, "%Y년 %m월 %d일")
        reviewdAt = date_obj.strftime("%Y-%m-%d")

        # get content
        content = comment.find_element(By.XPATH, "./div[1]").text

        # get usefulCount
        usefulCount = 0
        try:
            usefulCount = re.sub(
                r"[^0-9]",
                "",
                comment.find_element(By.XPATH, "./div[2]/div").text,
            )
        except:
            usefulCount = 0

        return userName, rating, reviewdAt, content, usefulCount

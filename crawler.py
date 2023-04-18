from bs4 import BeautifulSoup
import requests
from urllib.parse import quote


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

    def getInfoByname(self, name):
        pageInfo = self.playStore["listPage"]
        url = pageInfo["defaultUrl"] + quote(name) + pageInfo["basicQuery"]

        response = requests.get(url)
        self.soup = BeautifulSoup(response.content, "html.parser")

        container = self.soup.find("div", {"class": "XUIuZ"})

        if container == None:
            appId, title, madeBy = self._inCorrectQuery()
        else:
            appId, title, madeBy = self._correctQuery()

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

    def crawlComments(self, startDate, endDate, minStarredCount, maxStarredCount, howmany):
        
        

    # def _savePoint():

    # def checkprogressed():



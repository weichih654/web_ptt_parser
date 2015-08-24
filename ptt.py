#!/usr/bin/python
from HTMLParser import HTMLParser
import urllib2
import re
import sys

# create a subclass and override the handler methods
class PttLink:
    def __init__(self):
        self.type = ""
        self.link = ""
        self.content = ""

class PageInfo:
    def __init__(self):
        self.prevPage = ""
        self.nextPage = ""
        self.oldestPage = ""
        self.newestPage = ""

class PttParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__isWanted = False
        self.data = {} 
        self.data_list = [] 
        self.__thisValue = ""
        self.__urlPrefix = "https://www.ptt.cc/"
        self.__startGrab = False
        self.__isUnicode = False
        self.__thisType = ""
        self.__pageInfo = PageInfo()
        self.data["page_info"] = self.__pageInfo
    def handle_starttag(self, tag, attrs):
        if re.match(".*id.*prodlist.*", str(attrs)):
            self.__startGrab = True

        if re.match(".*r-list-container.*", str(attrs)):
            self.__startGrab = True
            self.__isUnicode = True

        if tag == "a":
            for value in attrs:
                result = re.match('\(\'href\', \'/bbs/.*\.html\'\)', str(value))
                isGroup = re.match('\(\'href\', \'/bbs/\d*\.html\'\)', str(value))
                isArticleList = re.match('\(\'href\', \'/bbs/.*\..*\..*\.html\'\)', str(value))

                if isGroup:
                    self.__thisType = "group"
                elif isArticleList:
                    self.__thisType = "article"
                else:
                    self.__thisType = "board"
 
                if result:
                    self.__isWanted = True
                    m = re.search('\(\'href\', \'(/bbs/.*\.html)\'\)', str(value))
                    url = m.group(1)
                    self.__thisValue = self.__urlPrefix + str(url)
                    break;
                else:
                    self.__thisValue = ""

        else:
            self.__isWanted = False

    def handle_data(self, data):
        if re.match(".*\xe4\xb8\x8a\xe9\xa0\x81.*", data):
            self.__pageInfo.prevPage = self.__thisValue
            self.data["page_info"] = self.__pageInfo
        elif re.match(".*\xe4\xb8\x8b\xe9\xa0\x81.*", data):
            self.__pageInfo.nextPage = self.__thisValue
            self.data["page_info"] = self.__pageInfo
        elif re.match(".*\xe6\x9c\x80\xe6\x96\xb0.*", data):
            self.__pageInfo.newestPage= self.__thisValue
            self.data["page_info"] = self.__pageInfo
        elif re.match(".*\xe6\x9c\x80\xe8\x88\x8a.*", data):
            self.__pageInfo.oldestPage= self.__thisValue
            self.data["page_info"] = self.__pageInfo

        if self.__isWanted and not re.match('^\s*$', data) and self.__startGrab:
            cont = ""
            if self.__isUnicode:
                cont = str(data)
            else:
                cont = str(data.decode("big5").encode("utf8"))
            pttLink = PttLink()
            pttLink.type = self.__thisType
            pttLink.link = self.__thisValue
            pttLink.content = cont
            self.data_list.append(pttLink)
        self.data["list"] = self.data_list

class Ptt:
    def __init__(self):
        return None

    def getBoardLists(self, url):
        response = urllib2.urlopen(url)
        html = response.read()
        boardListParser = PttParser()
        boardListParser.feed(html)

        return boardListParser.data

    def getBoardListsRange(self, url, offset, count):
        rangeDataList = []
        parseUrl = url

        getDataCounts = 0

        while getDataCounts < (offset + count):
            data = self.getBoardLists(parseUrl)
            for d in reversed(data["list"]):
                rangeDataList.append(d)

            getDataCounts = len(rangeDataList)
            if data["page_info"].nextPage is not None:
                parseUrl = data["page_info"].prevPage
            else:
                break

        return rangeDataList[offset:offset+count]

    def getArticleContent(self, url):
        response = urllib2.urlopen(url)
        html = response.read()
        head = html.find("<div id=\"main-container\">")
        tail = html.rfind("</div>")

        return html[head:tail]

if __name__ == '__main__':
    url = ""
    if len(sys.argv) < 3:
        print sys.argv[0], "[-a/-l] [url]"
        sys.exit(2)
    else:
        url = sys.argv[2]
    
    ptt = Ptt()
    if sys.argv[1] == "-l":
        boardLists = ptt.getBoardLists(url)
        for p in boardLists["list"]:
            print p.link, " : ", p.content, " type -> ", p.type
    
        print "prev = ", boardLists["page_info"].prevPage, " next = ", boardLists["page_info"].nextPage, "oldest = ", boardLists["page_info"].oldestPage, "newest = ", boardLists["page_info"].newestPage
    elif sys.argv[1] == "-r":
        boardLists = ptt.getBoardListsRange(url, int(sys.argv[3]), int(sys.argv[4]))
        for p in boardLists:
            print p.link, " : ", p.content, " type -> ", p.type
    else:
        articleContent = ptt.getArticleContent(url)
        print articleContent 


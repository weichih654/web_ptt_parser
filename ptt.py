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

class PttParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__isWanted = False
        self.data = [] 
        self.__thisValue = ""
        self.__urlPrefix = "https://www.ptt.cc/"
        self.__startGrab = False
        self.__isUnicode = False
        self.__thisType = ""
    def handle_starttag(self, tag, attrs):
        if re.match(".*id.*prodlist.*", str(attrs)):
            self.__startGrab = True

        if re.match(".*r-list-container.*", str(attrs)):
            self.__startGrab = True
            self.__isUnicode = True

        if tag == "a" and self.__startGrab:
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
            self.__isWanted = False

    def handle_data(self, data):
        if self.__isWanted and not re.match('^\s*$', data):
            cont = ""
            if self.__isUnicode:
                cont = str(data)
            else:
                cont = str(data.decode("big5").encode("utf8"))
            pttLink = PttLink()
            pttLink.type = self.__thisType
            pttLink.link = self.__thisValue
            pttLink.content = cont
            self.data.append(pttLink)

class Ptt:
    def __init__(self):
        return None

    def getBoardLists(self, url):
        response = urllib2.urlopen(url)
        html = response.read()
        boardListParser = PttParser()
        boardListParser.feed(html)

        return boardListParser.data

    def getArticleContent(self, url):
        response = urllib2.urlopen(url)
        html = response.read()
        head = html.find("<div id=\"main-container\">")
        tail = html.rfind("</div>")

        return html[head:tail]

url = ""
if len(sys.argv) < 3:
    print sys.argv[0], "[-a/-l] [url]"
    sys.exit(2)
else:
    url = sys.argv[2]

ptt = Ptt()
if sys.argv[1] == "-l":
    boardLists = ptt.getBoardLists(url)
    for p in boardLists:
        print p.link, " : ", p.content, " type -> ", p.type
else:
    articleContent = ptt.getArticleContent(url)
    print articleContent 


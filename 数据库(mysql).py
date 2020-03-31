import urllib.request

from bs4 import BeautifulSoup
import time
import threading
import random
import MySQLdb

user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
]


class MySpider:
    def open(self):
        self.con = MySQLdb.connect(host="127.0.0.1", port=3306, user='root', password="19980507",
                                   db="dangdangwang_books", charset='utf8')
        self.cursor = self.con.cursor()
        sql = "create table books (ID varchar(8) primary key,bTitle varchar(512),bAuthor varchar(128),bDate varchar(64),bPublisher varchar(128),bPrice varchar(16),bDetail text,bExt varchar(8))"
        try:
            self.cursor.execute(sql)
        except:
            self.cursor.execute("delete from books")
        self.count = 0
        self.page = 0
        self.TS = []

    def close(self):
        self.con.commit()
        self.con.close()

    def insert(self, ID, title, author, date, publisher, price, detail, ext):
        sql = "insert into books (ID,bTitle,bAuthor,bDate,bPublisher,bPrice,bDetail,bExt) values (%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cursor.execute(sql, [ID, title, author, date, publisher, price, detail, ext])

    def show(self):
        self.con = MySQLdb.connect(host="127.0.0.1", port=3306, user='root', password="19980507",
                                   db="dangdangwang_books", charset='utf8')
        self.cursor = self.con.cursor()
        self.cursor.execute("select ID,bTitle,bAuthor,bDate,bPublisher,bPrice,bDetail,bExt from books")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        print("Total ", len(rows))
        self.con.close()

    def spider(self, url):
        time.sleep(1)
        try:
            self.page += 1
            print("第", self.page, "页 ", url)
            headers = {'User-Agent': random.choice(user_agent)}
            req = urllib.request.Request(url=url, headers=headers)
            resp = urllib.request.urlopen(req)
            data = resp.read()
            html = data.decode("gbk")
            root = BeautifulSoup(html, "lxml")
            div = root.find("div", attrs={"class": "con shoplist"})
            ul = div.find("ul", attrs={"class": "bigimg"})
            lis = ul.find_all("li")

            for li in lis:
                title = li.find("a")["title"]
                spans = li.find("p", attrs={"class": "search_book_author"}).find_all("span")
                try:
                    author = spans[0].find("a").text
                except:
                    author = spans[0].text
                date = (spans[1].text).strip()
                date = date[1:]
                try:
                    publisher = spans[2].find("a").text
                except:
                    publisher = spans[2].text
                price = li.find("p", attrs={"class": "price"}).find("span").text
                detail = li.find("p", attrs={"class": "detail"}).text
                try:
                    src = li.find("a").find("img")["data-original"]
                except:
                    src = li.find("a").find("img")["src"]

                src = urllib.request.urljoin(url, src)
                p = src.rfind(".")
                ext = src[p:]
                self.count += 1
                ID = str(self.count)

                while len(ID) < 6:
                    ID = "0" + ID

                self.insert(ID, title, author, date, publisher, price, detail, ext)
                T = threading.Thread(target=self.download, args=[ID + ext, src])
                T.start()
                self.TS.append(T)

            if self.page < 54:

                li = root.find("div", attrs={"class": "paging"}).find("ul", attrs={"name": "Fy"}).find("li", attrs={
                    "class": "next"})
                try:
                    href = li.find("a")["href"]
                    url = urllib.request.urljoin(url, href)
                    # 递归调用spider
                    self.spider(url)
                except:
                    pass

        except Exception as err:

            print("spider: " + str(err))

    def download(self, fn, src):

        try:
            headers = {'User-Agent': random.choice(user_agent)}
            req = urllib.request.Request(url=src, headers=headers)
            resp = urllib.request.urlopen(req, timeout=5)
            data = resp.read()
            f = open("images\\" + fn, "wb")
            f.write(data)
            f.close()
            print("download ", fn)

        except Exception as err:
            print(fn + ":" + str(err))

    def process(self):

        url = "http://search.dangdang.com/?key=python"
        self.open()
        self.spider(url)
        self.close()
        for T in self.TS:
            T.join()


spider = MySpider()

while True:
    print("1.爬取")
    print("2.显示")
    print("3.退出")
    s = input("请选择(1,2,3):")

    if s == "1":
        print("Start.....")
        spider.process()
        print("Finished......")
    elif s == "2":
        spider.show()
    else:
        break

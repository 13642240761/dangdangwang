import urllib.request
from bs4 import BeautifulSoup
import time

def spider(url):
    global count, page
    #time.sleep(1)
    try:
        page += 1
        print("第", page, "页 ", url)
        resp = urllib.request.urlopen(url)
        data = resp.read()
        html = data.decode("gbk")
        root = BeautifulSoup(html, "lxml")
        div = root.find("div", attrs={"class": "con shoplist"})
        ul = div.find("ul", attrs={"class": "bigimg"})
        lis = ul.find_all("li")
        for li in lis:
            count += 1
            # 分析每个<li>中书籍信息：名称title、作者author、价格price、出版社publisher、简介detail、图像image
            p=li.find("p",attrs={"class":"search_book_author"})
            author=p.find("span").text

            print(count, author)
        li = root.find("div", attrs={"class": "paging"}).find("ul", attrs={"name": "Fy"}).find("li",attrs={"class": "next"})
        try:
            href = li.find("a")["href"]
            url = urllib.request.urljoin(url, href)
            # 递归调用spider
            spider(url)

        except:
            pass

    except Exception as err:
        print(err)

count = 0
page = 0
url = "http://search.dangdang.com/?key=python"
spider(url)
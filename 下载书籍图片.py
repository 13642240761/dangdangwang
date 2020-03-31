import urllib.request
from bs4 import BeautifulSoup
import time
import threading


def spider(url):
    global count, page,TS
    time.sleep(1)
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
            try:
                p = li.find("p", attrs={"class": "name"})
                title = p.find("a").text
                print(count, title)
                try:
                    src = li.find("a").find("img")["data-original"]
                except:
                    src = li.find("a").find("img")["src"]

                src=urllib.request.urljoin(url,src)
                #download(count,src)(慢)
                T=threading.Thread(target=download,args=[count,src])  #线程
                T.start()
                TS.append(T)
            except Exception as err:
                print("skip",count)

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


def download(count,src):
    try:
        p=src.rfind(".")
        ext=src[p:]
        fn=str(count)+ext
        resp=urllib.request.urlopen(src)
        data=resp.read()
        f=open("images\\"+fn,"wb")
        f.write(data)
        f.close()
        print("download",fn)
    except Exception as err:
        print(err)



count = 0
page = 0
TS=[]
url = "http://search.dangdang.com/?key=python"
spider(url)

for T in TS:
    T.join()
print("The end!!")











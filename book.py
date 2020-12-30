#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
from pathlib import Path
from typing import DefaultDict

import bs4
import requests
from PyPDF2 import PdfFileMerger


def scrape_urls():

    url = "http://pages.cs.wisc.edu/~remzi/OSTEP/#book-chapters"
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    base_url = "http://pages.cs.wisc.edu/~remzi/OSTEP/{}"
    with open("./urls.txt", "w+") as f:
        for link in soup.find_all("a", {"style": "color:black"}):
            print(base_url.format(link.attrs["href"]), file=f)


def scrape_urls2():

    url = "http://pages.cs.wisc.edu/~remzi/OSTEP/#book-chapters"
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    base_url = "http://pages.cs.wisc.edu/~remzi/OSTEP/{}"
    rslt = {}
    for link in soup.find_all("td"):
        el = link.find("small")
        small = link.find("small").get_text() if el else ""
        el = link.find("a")
        url = el.attrs["href"] if el and "href" in el.attrs else ""
        try:
            small = int(small)
            small = 100 + small
        except:
            small = None
        if small and url:
            rslt[small] = base_url.format(url)

    with open("./urls.txt", "w+") as f:
        for k in sorted(rslt.keys()):
            print(k, rslt[k], file=f)


def scrape_urls3():

    # get page
    bookurl = "http://pages.cs.wisc.edu/~remzi/OSTEP/#book-chapters"
    resp = requests.get(bookurl)
    soup = bs4.BeautifulSoup(resp.text, "html.parser")

    # parse page
    chapters = DefaultDict(list)
    chapter_base_url = "http://pages.cs.wisc.edu/~remzi/OSTEP/{}"
    for table in soup.find_all("table"):
        row_size = len(table)
        if row_size < 20:
            continue
        for row in table.find_all("tr"):
            current_column = 0
            for column in row.find_all("td"):
                chapter = column.find("a")
                if chapter:
                    chapters[current_column].append(
                        chapter_base_url.format(chapter.attrs["href"]))
                current_column = current_column + 1

    sort_key = 100
    with open("./urls.txt", "w+") as f:
        for column in chapters:
            for url in chapters[column]:
                print(sort_key, url, file=f)
                sort_key += 1


def download_book():
    def download(i, url):
        url = url.strip()
        print(f" {i} downloading {url}")
        res = requests.get(url, timeout=120)
        print(f"{res}")
        if res.ok:
            last_name = url.split("/")[-1]
            file_name = f"./output/{i}-{last_name}"
            if not file_name.endswith(".pdf"):
                file_name += ".pdf"
            print(f"{last_name}{file_name}")
            with open(f"{file_name}", "wb") as f:
                f.write(res.content)

    threads = []

    with open("./urls.txt") as f:
        for line in f:
            i, url = line.split(" ")
            print(f"{i}{url}")
            t = threading.Thread(target=download, args=(i, url))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()


def merge_pdf():
    output_dir = Path("./output")
    files = [file.resolve() for file in sorted(output_dir.glob("*.pdf"))]
    merger = PdfFileMerger()

    for pdf in files:
        merger.append(open(pdf, "rb"))

    with open("operating_system_three_easy_pieces.pdf", "wb") as fout:
        merger.write(fout)


def read_file():
    f = open("./urls3.txt")
    for i in f:
        index, url = i.split(" ")
        print(f"{index}{url}")


if __name__ == "__main__":
    scrape_urls3()
    download_book()
    merge_pdf()
    # read_file()

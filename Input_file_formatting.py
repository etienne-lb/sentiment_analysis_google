#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import glob, codecs
import html

def run() :
    # Reading all the CSV files
    files = glob.glob("data/*.xml")
    _output = "data_output/output_new.csv"
    _separator = ";"
    with codecs.open(_output, 'w', encoding="utf-8") as owt:
        row = ["id", "date", "message", "\n"]
        owt.write(_separator.join(row))
        for file in files :
            print("processing %s" % file)
            xml = codecs.open(file, encoding="utf-8").read()
            soup = BeautifulSoup(xml, "html.parser")
            chats = soup.findAll('chat')
            for chat in chats:
                id = chat.get('id')
                operator = chat.find("operator").text
                date = chat.find("datetime").text
                history = chat.find("history").findChildren()
                texts = []
                for h in history:
                    if h.name != "alert":
                        text = html.unescape(h.text)
                        text = text.replace(";", ",")
                        texts.append(text)
                text = ". ".join(texts)
                row = [str(id), date, operator, text, "\n"]
                owt.write(_separator.join(row))


if __name__ == "__main__" :
    run()
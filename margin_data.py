from bs4 import BeautifulSoup
import requests
import pandas as pd
from dataclasses import dataclass


@dataclass
class Margin:
    clearing_margin: int
    maintain_margin: int
    initial_margin: int


def create_margin(df, product):
    return Margin(
        clearing_margin=df["clearing_margin"][df["product"] == product].item(),
        maintain_margin=df["maintain_margin"][df["product"] == product].item(),
        initial_margin=df["initial_margin"][df["product"] == product].item(),
    )


# scrap data from TAIFEX "https://www.taifex.com.tw/cht/5/indexMarging"
url = "https://www.taifex.com.tw/cht/5/indexMarging"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")
table = soup.find("table")
df = pd.read_html(str(table))[0]

df = df.rename(
    columns={
        "商品別": "product",
        "結算保證金": "clearing_margin",
        "維持保證金": "maintain_margin",
        "原始保證金": "initial_margin",
    }
)
df = df.dropna()
df = df.reset_index(drop=True)


Tx = create_margin(df, "臺股期貨")
Mtx = create_margin(df, "小型臺指")
Txo_A = create_margin(df, "臺指選擇權風險保證金(A)值")
Txo_B = create_margin(df, "臺指選擇權風險保證金(B)值")

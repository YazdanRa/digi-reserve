from bs4 import BeautifulSoup as BS
import requests as req


def is_available(url):
    return True if BS(req.get(url).text, 'html.parser').find(buy_button) else False


def buy_button(tag):
    return True if tag.name == 'a' and tag.get_text() == 'افزودن به سبد خرید' else False

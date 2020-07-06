from bs4 import BeautifulSoup as BS
import requests as req

from processors.is_available import buy_button


def setup(url):
    session = start_session()
    # TODO: Login to account
    # TODO: Check limits
    add_to_cart(session, url)
    choose_time(session)


def start_session():
    s = req.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    })
    return s


def add_to_cart(session, url):
    product_url = BS(session.get(url).text, 'html.parser').find(buy_button)['href']
    session.get('https://digikala.com' + str(product_url))
    return


def choose_time(session):
    resp = session.get('https://digikala.com/shipping/')
    # TODO: Find the best time
    return

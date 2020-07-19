import re

from bs4 import BeautifulSoup as Bs
import requests


def setup(url, username, password):
    session = start_session()
    login(session, username, password)
    add_to_cart(session, url, 1)
    checkout(session)
    res, msg = check(session)
    session.close()
    return res


def start_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    })
    return s


def login(session, username, password):
    password_text = 'رمز عبور را وارد کنید'
    successful_login_text = 'سفارش‌های من'
    failed_login_text = r'\u0627\u0637\u0644\u0627\u0639\u0627\u062a \u06a9\u0627\u0631\u0628\u0631\u06cc \u0646\u0627\u062f\u0631\u0633\u062a \u0627\u0633\u062a'

    # username
    url = 'https://www.digikala.com/users/login-register/'
    r1_dom = Bs(session.get(url).text, 'html.parser')

    payload = {
        'login[email_phone]': username,
        'rc': r1_dom.select('input[name=rc]')[0]['value'],
        'rd': r1_dom.select('input[name=rd]')[0]['value'],
    }
    r2 = session.post(url, data=payload)
    if r2.status_code != 200:
        print('connection error, code: %s' % r2.status_code)
        return False

    # password
    if password_text in r2.text:
        r2_dom = Bs(r2.text, 'html.parser')

        payload = {
            'login[password]': password,
            'rc': r2_dom.select('input[name=rc]')[0]['value'],
            'rd': r2_dom.select('input[name=rd]')[0]['value'],
        }
        r3 = session.post(r2.url, data=payload)
        if r3.status_code != 200:
            print('connection error, code: %s' % r3.status_code)
            return False

        # succeed :)
        if successful_login_text in r3.text:
            print('successfully logged in')
            return True
        # wrong data :(
        elif failed_login_text in r3.text:
            print('wrong data!')
            return False
        # sth else :):
        else:
            print('unknown error')
            return False
    else:
        print('unknown error')
        return False


def add_to_cart(session, url, quantity):
    r1 = session.get(url)
    r1_dom = Bs(r1.text, 'html.parser')

    variation_id = re.search(
        r'/?cart/add/(\d+?)/1/?',
        r1_dom.select('a.btn-add-to-cart--full-width')[0]['href']).group(1)

    r2 = session.get(f'https://www.digikala.com/cart/add/{variation_id}/{quantity}', headers={
        'Referer': url,
        'X-Requested-With': 'XMLHttpRequest',
    }, params={
        'is_quick_view': 'true',
    })
    if r2.json()['status']:
        print('successfully added to cart')
    else:
        print('error')


def checkout(session):
    r1 = session.get('https://digikala.com/shipping/')
    r1_dom = Bs(r1.text, 'html.parser')
    best_time = min(
        [
            tag['value'] for tag in r1_dom.select(
                '.c-checkout-time-table__hour-checkbox:not(.c-outline-radio--disabled) input'
            )
        ]
    )
    parcel = r1_dom.select('.c-checkout-pack')[0]['data-parcel']
    data = {
        'shipping[skipItemIds]': r1_dom.select('input[name="shipping[skipItemIds]"]')[0]['value'],
        'shipping[type]': 'default',
        f'shipping-type-normal-{parcel}': 'express',
        f'shipping[time_scopes][{parcel}]': best_time,
        'is_legal': 0,
    }
    headers = {
        'Origin': 'https://digikala.com',
        'Referer': r1.url,
    }
    r2 = session.post(r1.url, data=data, headers=headers)
    r2_dom = Bs(r2.text, 'html.parser')
    payment = r2_dom.select('input[name=payment_method]:checked')[0]
    data = {
        'bank_id': payment['data-bank-id'],
        'payment_method': payment['value'],
    }
    headers = {
        'Origin': 'https://digikala.com',
        'Referer': r2.url,
    }
    session.post(r2.url, data=data, headers=headers)


def check(session):
    text = 'در صورت عدم پرداخت تا'
    url = 'https://www.digikala.com/profile/my-orders/'
    r = session.get(url)
    s = Bs(r.text, 'html.parser').findAll("div", {"class": "c-profile-order__warning"})
    msg = ''
    for item in s:
        msg += item.get_text()
    if text in r.text:
        return True, msg
    else:
        return False, ''

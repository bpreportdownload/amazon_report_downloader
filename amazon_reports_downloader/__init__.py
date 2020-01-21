import os
import sys
from sys import platform
import logging

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


from amazon_reports_downloader.signals import (
    get_shipping_fee_failure,
    pick_marketplace_failure,
    choose_template_failure,
    change_shipping_price_failure,
    trigger_report_request_failure,
    generate_report_failure
)


MARKETPLACE_MAPPING = {
    'us': {
        'sellercentral': 'sellercentral.amazon.com',
        'domain': 'www.amazon.com'
    },
    'ca': {
        'sellercentral': 'sellercentral.amazon.com',
        'domain': 'www.amazon.ca'
    },
    'mx': {
        'sellercentral': 'sellercentral.amazon.com',
        'domain': 'www.amazon.com.mx'
    },
    'uk': {
        'sellercentral': 'sellercentral.amazon.co.uk',
        'domain': 'www.amazon.co.uk'
    },
    'de': {
        'sellercentral': 'sellercentral.amazon.co.uk',
        'domain': 'www.amazon.de'
    },
    'fr': {
        'sellercentral': 'sellercentral.amazon.co.uk',
        'domain': 'www.amazon.fr'
    },
    'it': {
        'sellercentral': 'sellercentral.amazon.co.uk',
        'domain': 'www.amazon.it'
    },
    'es': {
        'sellercentral': 'sellercentral.amazon.co.uk',
        'domain': 'www.amazon.es'
    },
    'jp': {
        'sellercentral': 'sellercentral.amazon.co.jp',
        'domain': 'www.amazon.co.jp'
    },
    'au': {
        'sellercentral': 'sellercentral.amazon.com.au',
        'domain': 'www.amazon.com.au'
    },
    'in': {
        'sellercentral': 'sellercentral.amazon.in',
        'domain': 'www.amazon.in'
    },
    'cn': {
        'sellercentral': 'mai.amazon.cn',
        'domain': 'www.amazon.cn'
    }
}

SHIPPING_TEMPLATE_MAPPING = {
    'us': 'https://sellercentral.amazon.com/sbr/ref=xx_shipset_dnav_xx#shipping_templates',
    'uk': 'https://sellercentral.amazon.co.uk/sbr/ref=xx_shipset_dnav_xx#shipping_templates'
}

CUSTOM_PAYMENTS_REPORTS_MAPPING = {
    'us': "https://sellercentral.amazon.com/payments/reports/custom/request?tbla_daterangereportstable=sort:%7B%22sortOrder%22%3A%22DESCENDING%22%7D;search:undefined;pagination:1;",
}

bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
if platform.startswith('win32') or platform.startswith('cygwin'):
    driver_path = os.path.join(bin_dir, 'windows', 'chromedriver.exe')
elif platform.startswith('darwin'):
    driver_path = os.path.join(bin_dir, 'mac', 'chromedriver')
elif platform.startswith('linux'):
    driver_path = os.path.join(bin_dir, 'linux', 'chromedriver')
else:
    raise RuntimeError('Could not find chromedriver for platform {}'.format(platform))

shared_work_directory = os.path.join(os.path.expanduser('~'), '.amazon_seller_management')
if not os.path.isdir(shared_work_directory):
    os.makedirs(shared_work_directory)

drivers = dict()


def get_shared_driver(marketplace):
    marketplace = marketplace.upper()
    if drivers.get(marketplace, None):
        return drivers.get(marketplace)
    # data_dir = os.path.join(shared_work_directory, 'data')
    data_dir = os.path.join(shared_work_directory, marketplace)
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    opts = Options()
    opts.add_argument('-disable-web-security')
    opts.add_argument('-allow-running-insecure-content')
    opts.add_argument('--profile-directory={}'.format(marketplace))
    opts.add_argument('user-data-dir={}'.format(data_dir))
    opts.add_argument('--lang=en-us')

    caps = opts.to_capabilities()


    options = {
        'executable_path': driver_path,
        'desired_capabilities': caps,
    }
    driver = WebDriver(**options)
    driver.maximize_window()
    drivers[marketplace] = driver

    return driver


logger = logging.getLogger('AmazonSellerManagement')
formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


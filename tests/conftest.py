# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os

from amazon_management import get_shared_driver

import pytest

@pytest.fixture(scope='module')
def driver():
    driver = get_shared_driver('Test')
    yield driver
    driver.quit()

@pytest.fixture(scope='session')
def inventory_management_pages_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'pages', 'inventory_management')

@pytest.fixture(scope='session')
def inventory_management_homepage_urls(inventory_management_pages_dir):
    homepages = []
    for marketplace in ['us', 'ca', 'mx', 'uk', 'de', 'fr', 'it', 'es', 'jp', 'in', 'au', 'cn']:
        marketplace_dir = os.path.join(inventory_management_pages_dir, marketplace)
        index_path = os.path.join(marketplace_dir, 'index.html')
        if not os.path.isdir(marketplace_dir) or not os.path.isfile(index_path):
            continue

        homepages.append({'marketplace': marketplace, 'url': 'file://' + index_path})

    return homepages

@pytest.fixture(scope='session')
def payments_reports_pages_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'pages', 'payments_reports')

@pytest.fixture(scope='session')
def drr_report_generate_urls(payments_reports_pages_dir):
    drr_urls = []
    for marketplace in ['us', 'ca', 'mx', 'uk', 'de', 'fr', 'it', 'es', 'jp', 'in', 'au', 'cn']:
        marketplace_dir = os.path.join(payments_reports_pages_dir, marketplace)
        drr_page_path = os.path.join(marketplace_dir, 'request_report.html')
        if not os.path.isdir(marketplace_dir) or not os.path.isfile(drr_page_path):
            continue

        drr_urls.append({'marketplace': marketplace, 'url': 'file://' + drr_page_path})

    return drr_urls

@pytest.fixture(scope='session')
def target_inventory_details():
    return {
        'us': {
            'total_products_cnt': 2697217,
            'total_product_pages_cnt': 40
        }
    }

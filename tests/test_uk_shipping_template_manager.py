# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os

from amazon_management.shipping_template_managers import \
    UkShippingTemplateManager as ShippingTemplateManager
from amazon_management import driver_path

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

import pytest

@pytest.fixture(scope='module')
def shipping_templates_url():
    shipping_templates_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'pages', 'shipping_setting', 'uk', 'shipping_templates.html')

    return 'file://' + shipping_templates_file_path

@pytest.fixture(scope='module')
def shipping_template_edit_url():
    shipping_template_edit_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'pages', 'shipping_setting', 'uk', 'shipping_template_edit.html')

    return 'file://' + shipping_template_edit_file_path

@pytest.fixture(scope='module')
def driver():
    test_data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tmp', 'data')
    if not os.path.isdir(test_data_dir):
        os.makedirs(test_data_dir)

    opts = Options()
    opts.add_argument('–disable-web-security')
    opts.add_argument('–allow-running-insecure-content')
    opts.add_argument('--profile-directory=UK')
    opts.add_argument('user-data-dir={}'.format(test_data_dir))
    caps = opts.to_capabilities()

    options = {
        'executable_path': driver_path,
        'desired_capabilities': caps
    }
    driver = WebDriver(**options)
    yield driver

    driver.quit()

@pytest.fixture(scope='module')
def shipping_template_manager(driver):
    yield ShippingTemplateManager(driver)

def test_find_template_by_name(shipping_template_manager, shipping_templates_url):
    shipping_template_manager.driver.get(shipping_templates_url)

    template_name = 'Migrated Template'
    template_elem = shipping_template_manager.find_template_by_name(template_name)
    assert template_elem.get_attribute('title') == template_name

def test_choose_template(shipping_template_manager, shipping_templates_url):
    shipping_template_manager.driver.get(shipping_templates_url)

    template_name = 'Free shipping'
    template_elem = shipping_template_manager.find_template_by_name(template_name)
    assert shipping_template_manager.choose_template(template_elem)

def test_trigger_edit_template(shipping_template_manager, shipping_templates_url):
    shipping_template_manager.driver.get(shipping_templates_url)

    shipping_template_manager.trigger_edit_template()

    current_url = shipping_template_manager.driver.current_url
    assert current_url.find('/sbr/template#template/') != -1, current_url

def test_get_shipping_fee(shipping_template_manager, shipping_templates_url):
    shipping_template_manager.driver.get(shipping_templates_url)

    shipping_fees = shipping_template_manager.get_shipping_fee()
    assert len(shipping_fees) == 2

    target_shipping_fees = [
        {
            'per_order': '0.00',
            'per_item': '2.80'
        },
        {
            'per_order': '0.00',
            'per_item': '2.80'
        }
    ]
    assert target_shipping_fees == shipping_fees

# def test_get_standard_shipping_fees(shipping_template_manager, shipping_template_edit_url):
#     shipping_template_manager.driver.get(shipping_template_edit_url)
#     standard_shipping_fees = shipping_template_manager.get_standard_shipping_fees()
#     target_shipping_fees = [
#         {'per_order': 0.00, 'per_item': 2.80},
#         {'per_order': 0.00, 'per_item': 2.80}
#     ]

#     assert target_shipping_fees == standard_shipping_fees

# def test_set_standard_shipping_fees(shipping_template_manager, shipping_template_edit_url):
#     shipping_template_manager.driver.get(shipping_template_edit_url)
#     standard_shipping_fees = shipping_template_manager.get_standard_shipping_fees()
#     target_shipping_fees = [
#         {'per_order': 0.00, 'per_item': 2.80},
#         {'per_order': 0.00, 'per_item': 2.80}
#     ]
#     assert target_shipping_fees == standard_shipping_fees

#     shipping_fees = [
#         {'per_order': 3.99, 'per_item': 3.99},
#         {'per_order': 3.99, 'per_item': 3.99}
#     ]
#     shipping_template_manager.set_standard_shipping_fees(shipping_fees)

#     assert shipping_template_manager.check_standard_shipping_fees(shipping_fees)

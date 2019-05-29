# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import pdb

from amazon_management.inventory_manager import InventoryManager

import pytest


def test_inventory_manager(driver, inventory_management_homepage_urls, target_inventory_details):
    inv_manager = InventoryManager(driver)
    for homepage in inventory_management_homepage_urls:
        driver.get(homepage['url'])

        inv_detail = target_inventory_details.get(homepage['marketplace'])
        assert inv_manager.get_total_products_cnt() == inv_detail.get('total_products_cnt', 0)
        assert inv_manager.get_total_product_pages_cnt() == inv_detail.get('total_product_pages_cnt', 0)

        inv_manager.select_all()
        assert driver.find_element_by_css_selector(inv_manager.selectors['select_all_selector']).is_selected()
        enabled = driver.find_element_by_css_selector(
                inv_manager.selectors['bulk_action_select_selector']).is_enabled()
        if inv_detail.get('total_products_cnt', 0) > 0:
            assert enabled
        else:
            assert not enabled

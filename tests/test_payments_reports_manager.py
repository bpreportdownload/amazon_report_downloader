# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from amazon_management.payments_reports_manager import PaymentsReportsManager

import pytest


def test_inventory_manager(driver, drr_report_generate_urls):
    prm = PaymentsReportsManager(driver)
    for drr in drr_report_generate_urls:
        driver.get(drr['url'])

        assert prm.request_report('08/01/2019', '08/26/2019')

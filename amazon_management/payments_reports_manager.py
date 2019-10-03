# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import io
import datetime
import time
import json
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException)

from pydispatch.robust import sendRobust

from amazon_management import logger, shared_work_directory
from amazon_management.signals import (
    trigger_report_request_failure,
    generate_report_failure
)

def get_time_str():
    time_format = '%Y_%m_%d_%H_%M_%S'
    return datetime.datetime.now().strftime(time_format)

def save_page_source(file_name, page_source):
    webpages_dir = os.path.join(shared_work_directory, 'payments_reports', 'webpages')
    if not os.path.isdir(webpages_dir):
        os.makedirs(webpages_dir)

    file_path = os.path.join(webpages_dir, file_name)
    with io.open(file_path, 'w', encoding='utf-8', errors='ignore') as fh:
        fh.write(page_source)


class PaymentsReportsManager(object):
    def __init__(self, driver):
        self.driver = driver
        self.selectors = {
            'generate_report_btn': '#drrGenerateReportButton',
            'generate_report_modal': '#generateReportsModal',
            'report_range_radio_custom': '#drrReportRangeTypeRadioCustom',
            'drr_from_date': '#drrFromDate',
            'drr_to_date': '#drrToDate',
            'report_generate_btn': '#drrGenerateReportsGenerateButton'
        }

    def request_report(self, start_date, end_date):
        result = self.trigger_report_request()
        if not result:
            logger.debug('[Failed] Trigger report request!')

            return False

        logger.debug('[Succeed] Trigger report request!')

        result = self.generate_report(start_date, end_date)
        if result:
            logger.debug('[Succeed] Generate report request!')
        else:
            logger.debug('[Failed] Generate report request!')

        return result

    def trigger_report_request(self):
        result = False
        while True:
            try:
                gen_report_btn = WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.selectors['generate_report_btn'])))
                gen_report_btn.click()

                WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.selectors['generate_report_modal'])))

                result = True
                break
            except StaleElementReferenceException:
                pass
            except (NoSuchElementException, TimeoutException):
                save_page_source(
                    'trigger_report_request_{}.html'.format(get_time_str()),
                    self.driver.page_source)

                payload = {
                    'operation': 'trigger_report_request',
                    'exception': traceback.format_exc()
                }
                sendRobust(
                    signal=trigger_report_request_failure,
                    sender=self, message=json.dumps(payload))

        return result

    def generate_report(self, start_date, end_date):
        result = False

        while True:
            try:
                report_range_radio_custom = WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, self.selectors['report_range_radio_custom'])))
                report_range_radio_custom.click()
                time.sleep(0.5)
                report_range_radio_custom.click()

                time.sleep(1)

                drr_from_date_elem = WebDriverWait(self.driver, 7).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, self.selectors['drr_from_date'])))
                drr_from_date_elem.send_keys(start_date)

                time.sleep(1)

                drr_to_date_elem = WebDriverWait(self.driver, 7).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, self.selectors['drr_to_date'])))
                drr_to_date_elem.send_keys(end_date)

                report_generate_btn = WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, self.selectors['report_generate_btn'])))
                report_generate_btn.click()

                result = True

                break
            except StaleElementReferenceException:
                pass
            except (NoSuchElementException, TimeoutException):
                save_page_source(
                    'generate_report_{}.html'.format(get_time_str()),
                    self.driver.page_source)

                payload = {
                    'operation': 'generate_report',
                    'exception': traceback.format_exc()
                }
                sendRobust(
                    signal=generate_report_failure,
                    sender=self, message=json.dumps(payload))

        return result

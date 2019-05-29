# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException)
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys

from amazon_management import MARKETPLACE_MAPPING


class SellerLoginHelper(object):
    def __init__(self, driver, email, password, marketplace):
        self.driver = driver
        self.email = email
        self.password = password
        self.marketplace = marketplace.lower()

    def is_login_required(self):
        url = self.driver.current_url
        return url.find('/ap/signin') != -1

    def login(self):
        try:
            claimed_email_elem = self.driver.find_element_by_id('ap-claim')
            claimed_email = claimed_email_elem.get_attribute('value')

            if claimed_email.lower() != self.email.lower():
                add_account_elem = self.driver.find_element_by_id('cvf-account-switcher-add-accounts-link')
                self.br.get(add_account_elem.get_attribute('href'))
        except NoSuchElementException:
            pass

        try:
            email_elem = self.driver.find_element_by_id('ap_email')
            email_elem.clear()

            email_elem.send_keys(self.email)

            try:
                continue_elem = self.driver.find_element_by_id('continue')
                continue_elem.click()
            except NoSuchElementException:
                pass
        except NoSuchElementException:
            pass

        while True:
            try:
                try:
                    remember_elem = self.driver.find_element_by_name('rememberMe')
                    if not remember_elem.is_selected():
                        remember_elem.click()
                except NoSuchElementException:
                    pass

                password_elem = self.driver.find_element_by_id('ap_password')
                password_elem.clear()
                time.sleep(1)
                password_elem.send_keys(self.password)
                time.sleep(3)
                password_elem.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                break

    def pick_marketplace(self):
        result = True

        marketplace_domain = MARKETPLACE_MAPPING.get(self.marketplace)['domain']
        picker_xpath = '//select[@id="sc-mkt-picker-switcher-select"]'
        target_xpath = picker_xpath + '//option[contains(text(), "{}")]'.format(marketplace_domain)
        try:
            picker_elem = WebDriverWait(self.driver, 12).until(
                EC.presence_of_element_located((By.XPATH, picker_xpath)))
            picker_elem = Select(picker_elem)
            cur_marketplace = picker_elem.first_selected_option.text.strip()
            if cur_marketplace != marketplace_domain:
                picker_elem.select_by_visible_text(marketplace_domain)

            WebDriverWait(self.driver, 3).until(
                EC.element_located_to_be_selected((By.XPATH, target_xpath)))
        except (NoSuchElementException, TimeoutException) as e:
            result = False

        return result

# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import time
import datetime
import json
import io
import traceback

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from pydispatch.robust import sendRobust

from amazon_management import logger
from amazon_management import shared_work_directory
from amazon_management.signals import (
    get_shipping_fee_failure,
    pick_marketplace_failure,
    choose_template_failure,
    change_shipping_price_failure,
    get_standard_shipping_fees_failure,
    set_standard_shipping_fees_failure
)

def get_time_str():
    time_format = '%Y_%m_%d_%H_%M_%S'
    return datetime.datetime.now().strftime(time_format)

def save_page_source(file_name, page_source):
    webpages_dir = os.path.join(shared_work_directory, 'shipping', 'webpages')
    if not os.path.isdir(webpages_dir):
        os.makedirs(webpages_dir)

    file_path = os.path.join(webpages_dir, file_name)
    with io.open(file_path, 'w', encoding='utf-8', errors='ignore') as fh:
        fh.write(page_source)


class ShippingTemplateManager(object):
    def __init__(self, driver):
        self.driver = driver
        self.marketplace = ''
        self.marketplace_domain = ''

    def get_shipping_fee(self):
        raise NotImplementedError()

    def find_template_by_name(self, template_name, max_wait=90):
        raise NotImplementedError()

    def choose_template(self, template_elem):
        raise NotImplementedError()

    def trigger_edit_template(self, max_wait=60):
        raise NotImplementedError()

    def change_shipping_price(self, price_adjust):
        raise NotImplementedError()

    def get_standard_shipping_fees(self):
        result = []
        try:
            per_order_input_elem = WebDriverWait(self.driver, 90).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.selectors['css_domestic_per_order_input'])))
            while True:
                try:
                    per_order_prices = []
                    for per_order_input_elem in self.driver.find_elements(
                        By.CSS_SELECTOR, self.selectors['css_domestic_per_order_input']):
                        per_order_prices.append(
                            round(float(per_order_input_elem.get_attribute('value')), 2))
                    break
                except StaleElementReferenceException:
                    pass

            per_item_input_elem = WebDriverWait(self.driver, 90).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.selectors['css_domestic_per_item_input'])))
            while True:
                try:
                    per_item_prices = []
                    for per_item_input_elem in self.driver.find_elements(
                        By.CSS_SELECTOR, self.selectors['css_domestic_per_item_input']):
                        per_item_prices.append(
                            round(float(per_item_input_elem.get_attribute('value')), 2))
                    break
                except StaleElementReferenceException:
                    pass

            for idx, per_order_price in enumerate(per_order_prices):
                result.append({
                    'per_order': per_order_price,
                    'per_item': per_item_prices[idx]
                })
        except (NoSuchElementException, TimeoutException) as e:
            result = None

            logger.exception(e)

            save_page_source(
                'get_standard_shipping_fees_{}.html'.format(get_time_str()),
                self.driver.page_source)

            payload = {
                'operation': 'get_standard_shipping_fees',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(
                signal=get_standard_shipping_fees_failure, sender=self, message=json.dumps(payload))

        return result

    def set_standard_shipping_fees(self, shipping_fees):
        us_domestic_elem = self.driver.find_element_by_css_selector(
            self.selectors['css_domestic'])
        per_order_prices = [shipping_fee.get('per_order', None) for shipping_fee in shipping_fees]
        per_item_prices = [shipping_fee.get('per_item', None) for shipping_fee in shipping_fees]

        script = "var per_order_input_selector = '{}';".format(
            self.selectors['css_per_order_input'])
        for idx, per_order in enumerate(per_order_prices):
            if per_order is None:
                continue

            script += 'arguments[0].querySelectorAll(per_order_input_selector)[%d].dispatchEvent(new Event("click", {bubbles: true}));' % idx
            script += 'arguments[0].querySelectorAll(per_order_input_selector)[{}].value = {};'.format(idx, per_order)
            script += 'arguments[0].querySelectorAll(per_order_input_selector)[%d].dispatchEvent(new Event("change", {bubbles: true}));' % idx
            script += 'arguments[0].querySelectorAll(per_order_input_selector)[{}].blur();'.format(idx)

        script += "var per_item_input_selector = '{}';".format(
            self.selectors['css_per_item_input'])
        for idx, per_item in enumerate(per_item_prices):
            script += 'arguments[0].querySelectorAll(per_item_input_selector)[%d].dispatchEvent(new Event("click", {bubbles: true}));' % idx
            script += 'arguments[0].querySelectorAll(per_item_input_selector)[{}].value = {};'.format(idx, per_item)
            script += 'arguments[0].querySelectorAll(per_item_input_selector)[%d].dispatchEvent(new Event("change", {bubbles: true}));' % idx
            script += 'arguments[0].querySelectorAll(per_item_input_selector)[{}].blur();'.format(idx)

        try:
            self.driver.execute_script(script, us_domestic_elem)
        except Exception as e:
            logger.exception(e)
            logger.info('[set_standard_shipping_fees] %s', script)

            payload = {
                'operation': 'set_standard_shipping_fees', 'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(
                signal=set_standard_shipping_fees_failure, sender=self,
                message=json.dumps(payload))

    def check_standard_shipping_fees(self, shipping_fees):
        standard_shipping_fees = self.get_standard_shipping_fees()
        return standard_shipping_fees == shipping_fees

    def submit_price_change(self):
        # script = "var submit_btn = document.querySelector('{}');".format(self.selectors['css_submit'])
        # script += 'if (submit_btn.hasAttribute("disabled")) {'
        # script += "var submit_span = document.querySelector('{}');".format(
        #     self.selectors['css_submit_btn'])
        # script += 'if (submit_span.classList.contains("a-button-disabled")) {'
        # script += 'submit_span.classList.remove("a-button-disabled");'
        # script += '}'
        # script += 'submit_btn.removeAttribute("disabled");'
        # script += '}'
        # script += 'submit_btn.click()'
        script = "document.querySelector('{}').click()".format(self.selectors['css_submit'])
        try:
            self.driver.execute_script(script)
        except Exception as e:
            logger.exception(e)
            logger.info('[submit_price_change] %s', script)

            payload = {
                'operation': 'submit_price_change', 'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(
                signal=submit_price_change, sender=self,
                message=json.dumps(payload))


class UsShippingTemplateManager(ShippingTemplateManager):
    def __init__(self, driver):
        super(UsShippingTemplateManager, self).__init__(driver)

        self.marketplace = 'us'
        self.marketplace_domain = 'www.amazon.com'

        self.selectors = {
            'css_domestic': r'div#US_STANDARD\.DOMESTIC',
            'css_per_order_input': 'table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=pricePerOrder]',
            'css_per_item_input': 'table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=unitPrice]',
            'css_domestic_per_order_input': r'div#US_STANDARD\.DOMESTIC table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=pricePerOrder]',
            'css_domestic_per_item_input': r'div#US_STANDARD\.DOMESTIC table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=unitPrice]',
            'css_submit': '#submitButton-announce',
            'css_submit_btn': '#submitButton'
        }

    def get_shipping_fee(self):
        result = None

        shipping_rules_xpath = '//div[@id="serviceType~US_STANDARD.DOMESTIC"]'
        shipping_rules_xpath += '/table[contains(@class, "configRulesTable")]//tr'
        try:
            while True:
                try:
                    shipping_rule_elems = WebDriverWait(self.driver, 30).until(
                        EC.presence_of_all_elements_located((By.XPATH, shipping_rules_xpath)))
                    shipping_rule_elems.pop(0)
                    result = []
                    for shipping_rule_elem in shipping_rule_elems:
                        shipping_fee_elem = shipping_rule_elem.find_element_by_xpath(
                            './/td[last()]')
                        shipping_fee_text = shipping_fee_elem.text
                        shipping_fees = [part.strip().split(' ').pop(0).strip('$') for part in \
                            shipping_fee_text.split('+')]
                        result.append({'per_order': shipping_fees[0], 'per_item': shipping_fees[1]})

                    break
                except StaleElementReferenceException as e:
                    pass
        except (NoSuchElementException, TimeoutException) as e:
            logger.exception(e)

            save_page_source(
                'get_shipping_fee_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'get_shipping_fee',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(
                signal=get_shipping_fee_failure, sender=self, message=json.dumps(payload))

        return result

    def pick_marketplace(self):
        result = True

        picker_xpath = '//select[@id="sc-mkt-picker-switcher-select"]'
        target_xpath = picker_xpath + '//option[contains(text(), "{}")]'.format(
            self.marketplace_domain)
        try:
            picker_elem = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, picker_xpath)))
            picker_elem = Select(picker_elem)
            cur_marketplace = picker_elem.first_selected_option.text.strip()
            if cur_marketplace != self.marketplace_domain:
                picker_elem.select_by_visible_text(self.marketplace_domain)

            WebDriverWait(self.driver, 30).until(
                EC.element_located_to_be_selected((By.XPATH, target_xpath)))
        except (NoSuchElementException, TimeoutException) as e:
            result = False

            logger.exception(e)

            save_page_source(
                'pick_marketplace_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'pick_marketplace',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(signal=pick_marketplace_failure, sender=self, message=json.dumps(payload))

        return result

    def find_template_by_name(self, template_name, max_wait=90):
        template_xpath = '//div[@id="shippingTemplateLinks"]/' + \
            'div[contains(@class, "shipping_template_link")]//' + \
            'div[contains(@class, "template_name")][@title="{}"]'.format(template_name)
        try:
            template = WebDriverWait(self.driver, max_wait).until(
                EC.presence_of_element_located((By.XPATH, template_xpath)))
        except:
            template = None

        return template

    def choose_template(self, template_elem):
        if template_elem is None:
            return False

        result = True
        active_template_xpath = '//div[@id="shippingTemplateLinks"]/' + \
            'div[contains(@class, "shipping_template_link") and ' + \
            'contains(@class, "activate_template")]//' + \
            'div[contains(@class, "template_name")][@title="{}"]'.format(
                template_elem.get_attribute('title'))
        try:
            template_elem.click()
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, active_template_xpath)))
        except Exception as e:
            result = False

            logger.exception(e)

            save_page_source(
                'choose_template_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'choose_template',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(signal=choose_template_failure, sender=self, message=json.dumps(payload))

        return result

    def trigger_edit_template(self, max_wait=60):
        edit_btn_xpath = '//div[@id="template_actions"]//button'
        template_edit_btn = WebDriverWait(self.driver, max_wait).until(
            EC.presence_of_element_located((By.XPATH, edit_btn_xpath)))
        template_edit_btn.click()

    def change_shipping_price(self, price_adjust):
        result = True

        loading_image_xpath = '//div[@id="sbr_page_loading_image"]'
        add_rule_xpath = '//button[@id="US_STANDARD.DOMESTIC_addRuleButton-announce"]'
        domestic_region_xpath = '//div[@id="US_STANDARD.DOMESTIC"]//' + \
            'table[contains(@class, "configRulesTable")]/tbody/tr/td/div[contains(@class, "regions_name")]/' + \
            'div[contains(@class, "regions_name_left")]/span'
        try:
            WebDriverWait(self.driver, 180).until(
                EC.invisibility_of_element((By.XPATH, loading_image_xpath)))
            WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located((By.XPATH, add_rule_xpath)))

            region_elem = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, domestic_region_xpath)))

            cur_shipping_fees = self.get_standard_shipping_fees()
            # We won't change per order price for now
            shipping_fee_adjustments = []
            target_shipping_fees = []
            for cur_shipping_fee in cur_shipping_fees:
                per_item = round(cur_shipping_fee['per_item'] + price_adjust, 2)
                shipping_fee_adjustments.append({
                    'per_item': per_item
                })
                target_shipping_fees.append({
                    'per_order': cur_shipping_fee['per_order'],
                    'per_item': per_item
                })
            self.set_standard_shipping_fees(shipping_fee_adjustments)
            time.sleep(3)

            if self.check_standard_shipping_fees(target_shipping_fees):
                self.submit_price_change()
                time.sleep(7)
            else:
                cur_shipping_fees = self.get_standard_shipping_fees()
                msg = 'set standard shipping fees failed! Current: {}, Target: {}'.format(
                    str(cur_shipping_fees), str(target_shipping_fees))
                logger.error(msg)
                raise Exception(msg)
        except Exception as e:
            result = False

            logger.exception(e)

            save_page_source(
                'change_shipping_price_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'change_shipping_price',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(
                signal=change_shipping_price_failure, sender=self, message=json.dumps(payload))

        return result


class UkShippingTemplateManager(ShippingTemplateManager):
    def __init__(self, driver):
        super(UkShippingTemplateManager, self).__init__(driver)

        self.marketplace = 'uk'
        self.marketplace_domain = 'www.amazon.co.uk'

        self.selectors = {
            'css_domestic': r'div#EU_STANDARD\.DOMESTIC',
            'css_per_order_input': 'table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=pricePerOrder]',
            'css_per_item_input': 'table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=unitPrice]',
            'css_domestic_per_order_input': r'div#EU_STANDARD\.DOMESTIC table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=pricePerOrder]',
            'css_domestic_per_item_input': r'div#EU_STANDARD\.DOMESTIC table.configRulesTable ' + \
                'tbody tr td.shippingFee input[name=unitPrice]',
            'css_submit': '#submitButton-announce',
            'css_submit_btn': '#submitButton'
        }

    def get_shipping_fee(self):
        result = None

        shipping_rules_xpath = '//div[@id="serviceType~EU_STANDARD.DOMESTIC"]'
        shipping_rules_xpath += '/table[contains(@class, "configRulesTable")]//tr'
        try:
            while True:
                try:
                    shipping_rule_elems = WebDriverWait(self.driver, 30).until(
                        EC.presence_of_all_elements_located((By.XPATH, shipping_rules_xpath)))
                    shipping_rule_elems.pop(0)
                    result = []
                    for shipping_rule_elem in shipping_rule_elems:
                        shipping_fee_elem = shipping_rule_elem.find_element_by_xpath('.//td[last()]')
                        shipping_fee_text = shipping_fee_elem.text
                        shipping_fees = [part.strip().split(' ').pop(0).strip(u'£') for part in \
                            shipping_fee_text.split('+')]
                        result.append({'per_order': shipping_fees[0], 'per_item': shipping_fees[1]})
                    break
                except StaleElementReferenceException:
                    pass
        except (NoSuchElementException, TimeoutException) as e:
            logger.exception(e)

            save_page_source(
                'get_shipping_fee_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'get_shipping_fee',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(
                signal=get_shipping_fee_failure, sender=self, message=json.dumps(payload))

        return result

    def pick_marketplace(self):
        result = True

        picker_xpath = '//select[@id="sc-mkt-picker-switcher-select"]'
        target_xpath = picker_xpath + '//option[contains(text(), "{}")]'.format(
            self.marketplace_domain)
        try:
            picker_elem = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, picker_xpath)))
            picker_elem = Select(picker_elem)
            cur_marketplace = picker_elem.first_selected_option.text.strip()
            if cur_marketplace != self.marketplace_domain:
                picker_elem.select_by_visible_text(self.marketplace_domain)

            WebDriverWait(self.driver, 30).until(
                EC.element_located_to_be_selected((By.XPATH, target_xpath)))
        except (NoSuchElementException, TimeoutException) as e:
            result = False

            logger.exception(e)

            save_page_source(
                'pick_marketplace_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'pick_marketplace',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(signal=pick_marketplace_failure, sender=self, message=json.dumps(payload))

        return result

    def find_template_by_name(self, template_name, max_wait=90):
        template_xpath = '//div[@id="shippingTemplateLinks"]/' + \
            'div[contains(@class, "shipping_template_link")]//' + \
            'div[contains(@class, "template_name")][@title="{}"]'.format(template_name)
        try:
            template = WebDriverWait(self.driver, max_wait).until(
                EC.presence_of_element_located((By.XPATH, template_xpath)))
        except:
            template = None

        return template

    def choose_template(self, template_elem):
        if template_elem is None:
            return False

        result = True
        active_template_xpath = '//div[@id="shippingTemplateLinks"]/' + \
            'div[contains(@class, "shipping_template_link") and ' + \
            'contains(@class, "activate_template")]//' + \
            'div[contains(@class, "template_name")][@title="{}"]'.format(
                template_elem.get_attribute('title'))
        try:
            template_elem.click()
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, active_template_xpath)))
        except Exception as e:
            result = False

            logger.exception(e)

            save_page_source(
                'choose_template_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'choose_template',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(signal=choose_template_failure, sender=self, message=json.dumps(payload))

        return result

    def trigger_edit_template(self, max_wait=60):
        edit_btn_xpath = '//div[@id="template_actions"]//button'
        template_edit_btn = WebDriverWait(self.driver, max_wait).until(
            EC.presence_of_element_located((By.XPATH, edit_btn_xpath)))
        template_edit_btn.click()

    def change_shipping_price(self, price_adjust):
        result = True

        loading_image_xpath = '//div[@id="sbr_page_loading_image"]'
        add_rule_xpath = '//button[@id="EU_STANDARD.DOMESTIC_addRuleButton-announce"]'
        domestic_region_xpath = '//div[@id="EU_STANDARD.DOMESTIC"]//' + \
            'table[contains(@class, "configRulesTable")]/tbody/tr/td/div[contains(@class, "regions_name")]/' + \
            'div[contains(@class, "regions_name_left")]/span'
        try:
            WebDriverWait(self.driver, 180).until(
                EC.invisibility_of_element((By.XPATH, loading_image_xpath)))
            WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located((By.XPATH, add_rule_xpath)))

            region_elem = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, domestic_region_xpath)))

            cur_shipping_fees = self.get_standard_shipping_fees()
            # We won't change per order price for now
            shipping_fee_adjustments = []
            target_shipping_fees = []
            for cur_shipping_fee in cur_shipping_fees:
                per_item = round(cur_shipping_fee['per_item'] + price_adjust, 2)
                shipping_fee_adjustments.append({
                    'per_item': per_item
                })
                target_shipping_fees.append({
                    'per_order': cur_shipping_fee['per_order'],
                    'per_item': per_item
                })
            self.set_standard_shipping_fees(shipping_fee_adjustments)
            time.sleep(3)

            if self.check_standard_shipping_fees(target_shipping_fees):
                self.submit_price_change()
                time.sleep(7)
            else:
                cur_shipping_fees = self.get_standard_shipping_fees()
                msg = 'set standard shipping fees failed! Current: {}, Target: {}'.format(
                    str(cur_shipping_fees), str(target_shipping_fees))
                logger.error(msg)
                raise Exception(msg)
        except Exception as e:
            result = False

            logger.exception(e)

            save_page_source(
                'change_shipping_price_{}.html'.format(get_time_str()), self.driver.page_source)

            payload = {
                'operation': 'change_shipping_price',
                'marketplace': self.marketplace,
                'exception': traceback.format_exc()
            }
            sendRobust(
                signal=change_shipping_price_failure, sender=self, message=json.dumps(payload))

        return result

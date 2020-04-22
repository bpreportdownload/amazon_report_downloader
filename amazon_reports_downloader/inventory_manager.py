import time
import random
import re
import os
import requests
import calendar
import traceback
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from json import dumps
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.select import Select
from selenium import webdriver
from amazon_reports_downloader import logger

class Download(object):
    def __init__(self, driver):
        self.driver = driver
        self.selectors = {
            'total_products_selector': '#mt-header-count-value',
            'total_product_pages_selector': 'span.mt-totalpagecount',
            'page_input_selector': 'input#myitable-gotopage',
            'go_to_page_selector': '#myitable-gotopage-button > span > input',
            'select_all_selector': '#mt-select-all',
            'bulk_action_select_selector': 'div.mt-header-bulk-action select',
            'option_delete_selector': 'option#myitable-delete',
            'continue_selector': '#interstitialPageContinue-announce',
            'email': '#email',
            'password': '#password',
            'login': 'body > div.container-fluid > div > div > div > div > div > div > div.panel-body > form > div:nth-child(5) > div > button',
            'seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(1) > div > div > div.panel-body > form > div:nth-child(4) > div > select',
            'order_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(1) > div > div > div.panel-body > form > div:nth-child(4) > div > select',
            'finance_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(4) > div > select',
            'FBA_shipments_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(2) > div > div > div.panel-body > form > div:nth-child(4) > div > select',
                                             # '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(2) > div > div > div.panel-body > form > div:nth-child(4) > div > select'
            'ads_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(4) > div > select',
            'campaigns_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div > div > div:nth-child(1) > div.panel-body > form > div:nth-child(4) > div > select',
            'searchterms_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div > div > div:nth-child(2) > div.panel-body > form > div:nth-child(4) > div > select',
            'orders_import': '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(1) > div > div > div.panel-body > form > div:nth-child(6) > div > button',
            'finance_import': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(7) > div > button',
            'FBA_shipments_import': '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(2) > div > div > div.panel-body > form > div:nth-child(6) > div > button',
            'listings_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(4) > div > select',
            'FBA_inventory_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(4) > div > select',
            'business_seller_selector': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(4) > div > select',
            'order_shipments_import': '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(2) > div > div > div.panel-body > form > div:nth-child(6) > div > button',
            'campaigns_import': '#page-content-wrapper > div:nth-child(3) > div > div > div > div:nth-child(1) > div.panel-body > form > div:nth-child(8) > div > button',
            'ads_import': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(7) > div > button',
            'searchterms_import': '#page-content-wrapper > div:nth-child(3) > div > div > div > div:nth-child(2) > div.panel-body > form > div:nth-child(7) > div > button',
            'ads_country': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(5) > div > select',
            'finance_country': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(5) > div > select',
            'campaigns_country': '#page-content-wrapper > div:nth-child(3) > div > div > div > div:nth-child(1) > div.panel-body > form > div:nth-child(5) > div > select',
            'searchterms_country': '#page-content-wrapper > div:nth-child(3) > div > div > div > div:nth-child(2) > div.panel-body > form > div:nth-child(5) > div > select',
            'listings_country': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(5) > div > select',
            'FBA_inventory_country': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(5) > div > select',
            'business_country': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(6) > div > select',
            'campaigns_date': '#page-content-wrapper > div:nth-child(3) > div > div > div > div:nth-child(1) > div.panel-body > form > div:nth-child(6) > div > input[type=date]',
            'business_date': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(5) > div > input[type=date]',
            'listings_import': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(7) > div > button',
            'FBA_inventory_import': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(7) > div > button',
            'business_import': '#page-content-wrapper > div:nth-child(3) > div > div > div > div > div.panel-body > form > div:nth-child(8) > div > button',
            'order_report': '#sc-navtab-reports',
            'FBA_shipment_report': '',
            'finance_report': '',
            'advertising_report': '',
            'campaigns_bulk_report': '',
            'advertising_search_term_report': '',
            'listings_report': '',
            'FBA_inventory_report': '',
            'business_report': '',
        }

    def add_inventory(self, marketplace, seller_id, sku, units, package_l, package_w, package_h, package_weight, shipment_name, shipment_number, shipment_id, start):
        time.sleep(random.randint(4, 7))
        logger.info("shipment_id: " + shipment_id)
        logger.info("start: " + str(start))
        logger.info("shipment_number: " + str(shipment_number))
        logger.info("shipment_name: " + shipment_name)
        first_window = self.driver.current_window_handle
        for index in range(start, shipment_number):
            logger.info("index: " + str(index))
            if index > 0:
                self.driver.execute_script("window.open();")
                # Switch to the new window
                self.driver.switch_to.window(self.driver.window_handles[index])
                self.driver.get("https://sellercentral.amazon.{marketplace}/gp/homepage.html/ref=xx_home_logo_xx".format(
                    marketplace=marketplace))
                logger.info("https://sellercentral.amazon.{marketplace}/gp/homepage.html/ref=xx_home_logo_xx".format(
                    marketplace=marketplace))
                time.sleep(random.randint(4, 7))

            try:
                # 移动鼠标到inventory
                for i in range(0, 3):
                    click = 'false'
                    try:
                        inventory = WebDriverWait(self.driver, 40, 0.5).until(
                            EC.presence_of_element_located((By.ID, 'sc-navtab-inventory')))
                        time.sleep(random.randint(4, 7))
                        webdriver.ActionChains(self.driver).move_to_element(inventory).perform()
                        logger.info('go to inventory')

                        # click inventory reports

                        length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-inventory"]/ul/li'))
                        logger.info(length)
                        for i in range(1, length):
                            report_name = self.driver.find_element_by_xpath(
                                '//*[@id="sc-navtab-inventory"]/ul/li[{}]'.format(i)).text.strip()
                            if report_name.startswith('Manage Inventory'):
                                time.sleep(random.randint(7, 9))
                                js_click_inventory_reports = "document.querySelector('#sc-navtab-inventory > ul > li:nth-child({}) > a').click();".format(
                                    i)
                                self.driver.execute_script(js_click_inventory_reports)
                                logger.info('click Manage Inventory')
                                time.sleep(random.randint(1, 5))
                                click = 'true'
                                break
                        if click == 'true':
                            break
                    except Exception as e:
                        print(e)
                sku_search_input = self.driver.find_element_by_id('myitable-search')
                sku_search_input.send_keys(sku)
                time.sleep(random.randint(1, 3))
                js_click_search = "document.querySelector('#myitable-search-button > span > input').click();"
                self.driver.execute_script(js_click_search)
                logger.info('try to find this item ' + sku)
                time.sleep(random.randint(4, 7))
                try:
                    dropdown = WebDriverWait(self.driver, 40, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#myitable > div.mt-content.clearfix > div > table > tbody > tr.mt-row > td:nth-child(17) > div.mt-save-button-dropdown-normal > span > span > span.a-button.a-button-group-last.a-button-splitdropdown > span > button')))
                    webdriver.ActionChains(self.driver).move_to_element(dropdown).perform()
                    time.sleep(random.randint(1, 4))
                    logger.info('go to dropdown')

                    try:
                        js_click_dropdown = "document.querySelector('#myitable > div.mt-content.clearfix > div > table > tbody > tr.mt-row > td:nth-child(17) > div.mt-save-button-dropdown-normal > span > span > span.a-button.a-button-group-last.a-button-splitdropdown > span > button').click();"
                        self.driver.execute_script(js_click_dropdown)

                    except Exception as e:
                        print(e)

                    time.sleep(random.randint(2, 4))
                except Exception as e:
                    print(e)
                    logger.info('can not find this item ' + sku)
                    return
                try:
                    length = len(self.driver.find_elements_by_xpath('//*[@id="a-popover-1"]/div/div/ul/li'))
                    logger.info('The length of the list is ' + str(length))
                except Exception as e:
                    print(e)
                    try:
                        self.driver.find_element_by_css_selector(
                            '#myitable > div.mt-content.clearfix > div > table > tbody > tr.mt-row > td:nth-child(17) > div.mt-save-button-dropdown-normal > span > span > span.a-button.a-button-group-last.a-button-splitdropdown > span > button').click()
                        time.sleep(random.randint(2, 4))
                        length = len(self.driver.find_elements_by_xpath('//*[@id="a-popover-1"]/div/div/ul/li'))
                    except Exception as e:
                        print(e)
                js_click_flag = False
                for i in range(1, length):
                    dropdown_name = self.driver.find_element_by_xpath(
                        '//*[@id="a-popover-1"]/div/div/ul/li[{}]'.format(i)).text.strip()
                    logger.info(dropdown_name + ' ' + str(i))
                    if dropdown_name.startswith('Send'):
                        logger.info(dropdown_name + ' ' + str(i))
                        time.sleep(random.randint(1, 5))
                        try:
                            js_click_send = "document.querySelector('#a-popover-1 > div > div > ul > li:nth-child({}) > a').click();".format(i)
                            self.driver.execute_script(js_click_send)
                            js_click_flag = True
                        except Exception as e:
                            print(e)

                        logger.info('click Send/Replenish Inventory')
                        time.sleep(random.randint(3, 7))
                        break
                if not js_click_flag:
                    try:
                        js_click_send = "document.querySelector('#dropdown1_5').click();".format(i)
                        self.driver.execute_script(js_click_send)
                    except Exception as e:
                        print(e)
                time.sleep(random.randint(5, 7))
                try:
                    WebDriverWait(self.driver, 40, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        '#save-manifest')))
                    continue_ele = self.driver.find_element_by_css_selector("#save-manifest")
                    if continue_ele.is_enabled():
                        js_click_send = "document.querySelector('#save-manifest').click();"
                        self.driver.execute_script(js_click_send)
                        time.sleep(random.randint(3, 7))
                except Exception as e:
                    print(e)
                    try:
                        self.driver.find_element_by_css_selector(
                            '#fba-core-page > div.fba-core-page-meta-landing-page.fba-core-page-meta-container > div.action > span:nth-child(2) > button').click()
                    except Exception as e:
                        print(e)
                logger.info('config Send')
                try:
                    limit = self.driver.find_element_by_css_selector('#plan-items > tr:nth-child(2) > td.item-errors.info > p.fba-core-alert-label.fba-core-alert-label-error').text.strip()
                    if limit == "Limited restock":
                        logger.info('Limited restock')
                        break
                except Exception as e:
                    print(e)

                try:

                    logger.info('length')
                    length_ele = self.driver.find_element_by_css_selector(
                        '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(1)')
                    length_ele.clear()
                    length_ele.send_keys(package_l)
                    logger.info('w')
                    wide_ele = self.driver.find_element_by_css_selector(
                        '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(2)')

                    wide_ele.clear()
                    wide_ele.send_keys(package_w)
                    logger.info('h')
                    height_ele = self.driver.find_element_by_css_selector(
                        '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(3)')

                    height_ele.clear()
                    height_ele.send_keys(package_h)

                    logger.info('weight')
                    weight_ele = self.driver.find_element_by_css_selector('#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(6) > form > input')

                    js_click_weight = "document.querySelector('#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(6) > form > select').value = 'G';"
                    self.driver.execute_script(js_click_weight)
                    weight_ele.send_keys(package_weight)

                    WebDriverWait(self.driver, 40, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        '#save-item-catalog-attributes')))

                    logger.info('begin to save')
                    js_click_save = "document.querySelector('#save-item-catalog-attributes').click();"
                    self.driver.execute_script(js_click_save)
                    logger.info('save done')
                    time.sleep(random.randint(4, 7))

                except Exception as e:
                    print(e)
                    print("do not need to add dimension")
                self.driver.find_element_by_css_selector(
                    '#batch-update-number-cases').send_keys(
                    units)
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#continue-plan')))
                js_click_continue = "document.querySelector('#continue-plan').click();".format(
                    i)
                self.driver.execute_script(js_click_continue)

                time.sleep(random.randint(4, 7))
                try:
                    logger.info('click choose category')
                    WebDriverWait(self.driver, 40, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        '#prep-items > tr:nth-child(2) > td.prep-category > a')))
                    js_click_choose_category = "document.querySelector('#prep-items > tr:nth-child(2) > td.prep-category > a').click();"
                    self.driver.execute_script(js_click_choose_category)

                    logger.info('choose last one')

                    js_click_choose_no = "document.querySelector('#prep-categories').value = 'NONE';"
                    self.driver.execute_script(js_click_choose_no)
                    time.sleep(random.randint(1, 4))

                    logger.info('click choose')
                    js_click_choose = "document.querySelector('#choose-category-button').click();"
                    self.driver.execute_script(js_click_choose)
                    time.sleep(random.randint(4, 7))
                except Exception as e:
                    print(e)

                try:
                    logger.info('click continue')
                    js_click_continue = "document.querySelector('#continue-plan').click();"

                    self.driver.execute_script(js_click_continue)
                    time.sleep(random.randint(4, 7))
                except Exception as e:
                    print(e)

                for i in range(5):
                    try:
                        element = self.driver.find_element_by_css_selector("#continue-plan")
                        logger.info(element.is_enabled())
                        if element.is_enabled():
                            logger.info('click continue agin')
                            js_click_continue = "document.querySelector('#continue-plan').click();"
                            self.driver.execute_script(js_click_continue)
                            time.sleep(random.randint(2, 5))

                        if not element.is_enabled() and i < 2:
                            logger.info('continue is disabled')
                            js_click_all_products = "document.querySelector('#fba-core-tabs > li:nth-child(2) > a').click();"
                            self.driver.execute_script(js_click_all_products)
                            time.sleep(random.randint(2, 5))
                            logger.info('click products needs info')
                            try:

                                logger.info('length')
                                length_ele = self.driver.find_element_by_css_selector(
                                    '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(1)')
                                length_ele.clear()
                                length_ele.send_keys(package_l)
                                logger.info('w')
                                wide_ele = self.driver.find_element_by_css_selector(
                                    '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(2)')

                                wide_ele.clear()
                                wide_ele.send_keys(package_w)
                                logger.info('h')
                                height_ele = self.driver.find_element_by_css_selector(
                                    '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(3)')

                                height_ele.clear()
                                height_ele.send_keys(package_h)

                                logger.info('weight')
                                weight_ele = self.driver.find_element_by_css_selector(
                                    '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(6) > form > input')

                                js_click_weight = "document.querySelector('#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(6) > form > select').value = 'G';"
                                self.driver.execute_script(js_click_weight)
                                weight_ele.send_keys(package_weight)

                                time.sleep(random.randint(1, 4))

                                logger.info('begin to save')
                                js_click_save = "document.querySelector('#save-item-catalog-attributes').click();"
                                self.driver.execute_script(js_click_save)
                                logger.info('save done')
                                time.sleep(random.randint(4, 7))

                            except Exception as e:
                                print(e)
                                print("do not need to add dimension")
                            tot_ele = self.driver.find_element_by_css_selector(
                                '#batch-update-number-cases')
                            tot_ele.clear()
                            tot_ele.send_keys(
                                units)

                            num_ele = self.driver.find_element_by_css_selector(
                                "#plan-items > tr:nth-child(2) > td.number.indi-pack > input")
                            num_ele.clear()
                            num_ele.send_keys(
                                units)
                            logger.info('send value')
                            time.sleep(random.randint(4, 7))
                            logger.info('click continue agin')
                            js_click_continue = "document.querySelector('#continue-plan').click();"
                            self.driver.execute_script(js_click_continue)
                            time.sleep(random.randint(4, 7))
                        try:
                            element = self.driver.find_element_by_css_selector("#continue-plan")
                            logger.info(element.is_enabled())
                            if not element.is_enabled() and i > 1:
                                logger.info('continue is disabled')
                                js_click_all_products = "document.querySelector('#fba-core-tabs > li:nth-child(1) > a').click();"
                                self.driver.execute_script(js_click_all_products)
                                time.sleep(random.randint(4, 7))
                                logger.info('click all products')
                                try:
                                    js_click_length = "document.querySelector('#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > select').value = 'CM';"
                                    self.driver.execute_script(js_click_length)

                                    logger.info('length')
                                    length_ele = self.driver.find_element_by_css_selector(
                                        '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(1)')
                                    length_ele.clear()
                                    length_ele.send_keys(package_l)
                                    logger.info('w')
                                    wide_ele = self.driver.find_element_by_css_selector(
                                        '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(2)')

                                    wide_ele.clear()
                                    wide_ele.send_keys(package_w)
                                    logger.info('h')
                                    height_ele = self.driver.find_element_by_css_selector(
                                        '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(3) > form > input:nth-child(3)')

                                    height_ele.clear()
                                    height_ele.send_keys(package_h)

                                    logger.info('weight')
                                    weight_ele = self.driver.find_element_by_css_selector(
                                        '#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(6) > form > input')

                                    js_click_weight = "document.querySelector('#plan-items > tr:nth-child(2) > td.item-errors.info > div:nth-child(6) > form > select').value = 'G';"
                                    self.driver.execute_script(js_click_weight)
                                    weight_ele.send_keys(package_weight)

                                    time.sleep(random.randint(4, 7))

                                    logger.info('begin to save')
                                    js_click_save = "document.querySelector('#save-item-catalog-attributes').click();"
                                    self.driver.execute_script(js_click_save)
                                    logger.info('save done')
                                    time.sleep(random.randint(4, 7))

                                except Exception as e:
                                    print(e)
                                    print("do not need to add dimension")
                                tot_ele = self.driver.find_element_by_css_selector(
                                    '#batch-update-number-cases')
                                tot_ele.clear()
                                tot_ele.send_keys(
                                    units)

                                num_ele = self.driver.find_element_by_css_selector(
                                    "#plan-items > tr:nth-child(2) > td.number.indi-pack > input")
                                num_ele.clear()
                                num_ele.send_keys(
                                    units)
                                logger.info('send value')
                                time.sleep(random.randint(4, 7))
                                logger.info('click continue agin')
                                js_click_continue = "document.querySelector('#continue-plan').click();"
                                self.driver.execute_script(js_click_continue)
                                time.sleep(random.randint(4, 7))
                        except Exception as e:
                            print(e)
                    except Exception as e:
                        print(e)
                logger.info(index)
                logger.info(shipment_id)
                if index == 0:
                    logger.info(shipment_name)
                    elem = self.driver.find_element_by_css_selector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(1) > input.fba-core-input.fba-core-input-large.new-shipment-name.fba-core-input-text')
                    elem.clear()
                    elem.send_keys(shipment_name)
                    time.sleep(random.randint(1, 5))

                    # js_click_continue = "document.querySelector('#fba-inbound-manifest-workflow-preview-edit-create-shipments').click();"
                    # self.driver.execute_script(js_click_continue)
                    # logger.info('confirm')
                    # time.sleep(random.randint(8, 12))
                    # try:
                    #     shipment_id = self.driver.find_element_by_css_selector("#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(2)").text.strip()
                    #
                    #     logger.info("css" + shipment_id)
                    # except Exception as e:
                    #     print(e)
                    #
                    # try:
                    #     shipment_id = self.driver.find_element_by_xpath(
                    #         "//*[@id='fba-core-workflow-shipment-summary-shipment']/tr[1]/td[2]").text.strip()
                    #
                    #     logger.info("xpath" + shipment_id)
                    # except Exception as e:
                    #     print(e)
                    #
                    # try:
                    #     shipment_id = self.driver.find_element_by_xpath(
                    #         "/html/body/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[1]/td[2]").text.strip()
                    #
                    #     logger.info("full" + shipment_id)
                    # except Exception as e:
                    #     print(e)
                else:
                    pass
                    # js_click_continue = "document.querySelector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(2) > input').click();"
                    # self.driver.execute_script(js_click_continue)
                    # time.sleep(random.randint(1, 5))
                    # logger.info(shipment_id)
                    # try:
                    #     js_click_continue = "document.querySelector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(2) > select').value = " + shipment_id + ";"
                    #     logger.info(js_click_continue)
                    #
                    #
                    #     self.driver.execute_script(js_click_continue)
                    # except Exception as e:
                    #     print(e)
                    #
                    # try:
                    #     js_click_continue = "document.querySelector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(2) > select').value = " + shipment_id
                    #     logger.info(js_click_continue)
                    #     logger.info("no")
                    #     self.driver.execute_script(js_click_continue)
                    # except Exception as e:
                    #     print(e)
                    # try:
                    #     js_click_continue = "document.querySelector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(2) > select').value = " + dumps(shipment_id)
                    #     logger.info(js_click_continue)
                    #     logger.info("dumps")
                    #
                    #     self.driver.execute_script(js_click_continue)
                    # except Exception as e:
                    #     print(e)
                    # time.sleep(random.randint(1, 5))
                    #
                    # js_click_continue = "document.querySelector('#fba-inbound-manifest-workflow-preview-edit-create-shipments').className = 'amznBtn btn-lg-pri-arrowr';"
                    # self.driver.execute_script(js_click_continue)
                    # time.sleep(random.randint(1, 5))
                    #
                    # js_click_continue = "document.querySelector('#fba-inbound-manifest-workflow-preview-edit-create-shipments').disabled = false;"
                    # self.driver.execute_script(js_click_continue)
                    # time.sleep(random.randint(1, 5))

            except Exception as e:
                print(e)
        self.driver.switch_to_window(first_window)
        js_click_continue = "document.querySelector('#fba-inbound-manifest-workflow-preview-edit-create-shipments').click();"
        self.driver.execute_script(js_click_continue)
        logger.info('confirm')
        time.sleep(random.randint(3, 5))
        WebDriverWait(self.driver, 40, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(2)')))

        try:
            shipment_id = self.driver.find_element_by_css_selector("#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(2)").text.strip()

            logger.info("css" + shipment_id)
        except Exception as e:
            print(e)

        try:
            shipment_id = self.driver.find_element_by_xpath(
                "//*[@id='fba-core-workflow-shipment-summary-shipment']/tr[1]/td[2]").text.strip()

            logger.info("xpath" + shipment_id)
        except Exception as e:
            print(e)

        try:
            shipment_id = self.driver.find_element_by_xpath(
                "/html/body/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div/div/div[2]/div/div/table/tbody/tr[1]/td[2]").text.strip()

            logger.info("full" + shipment_id)
        except Exception as e:
            print(e)
        for index in range(shipment_number - 1, start - 1, -1):
            try:

                if index > 0:
                    self.driver.switch_to.window(self.driver.window_handles[index])
                    # Switch to the new window

                    self.driver.refresh()
                    time.sleep(random.randint(1, 3))
                    WebDriverWait(self.driver, 40, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(2) > input')))

                    js_click_continue = "document.querySelector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(2) > input').click();"
                    self.driver.execute_script(js_click_continue)
                    time.sleep(random.randint(1, 5))
                    logger.info(shipment_id)
                    try:
                        js_click_continue = "document.querySelector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(1) > ul > li:nth-child(2) > select').value = " + dumps(
                            shipment_id)
                        logger.info(js_click_continue)
                        logger.info("dumps")

                        self.driver.execute_script(js_click_continue)
                    except Exception as e:
                        print(e)
                    time.sleep(random.randint(1, 5))

                    js_click_continue = "document.querySelector('#fba-inbound-manifest-workflow-preview-edit-create-shipments').className = 'amznBtn btn-lg-pri-arrowr';"
                    self.driver.execute_script(js_click_continue)

                    js_click_continue = "document.querySelector('#fba-inbound-manifest-workflow-preview-edit-create-shipments').disabled = false;"
                    self.driver.execute_script(js_click_continue)

                    js_click_continue = "document.querySelector('#fba-inbound-manifest-workflow-preview-edit-create-shipments').click();"
                    self.driver.execute_script(js_click_continue)
                    time.sleep(random.randint(2, 4))
                    self.driver.close()
                else:
                    self.driver.switch_to_window(first_window)
                    WebDriverWait(self.driver, 40, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        '#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(6) > button')))

                    js_click_continue = "document.querySelector('#fba-core-workflow-shipment-summary-shipment > tr:nth-child(1) > td:nth-child(6) > button').click();"
                    self.driver.execute_script(js_click_continue)
                    time.sleep(random.randint(1, 3))
                    self.driver.close()
            except Exception as e:
                print(e)


    def listing_info_scrapy(self, marketplace, seller_id, seller_profit_domain):
        try:
            self.driver.get("https://www.amazon.{marketplace}/s?me={seller_id}&marketplaceID=ATVPDKIKX0DER".format(marketplace=marketplace, seller_id=seller_id))
            logger.info("https://www.amazon.{marketplace}/s?me={seller_id}&marketplaceID=ATVPDKIKX0DER".format(marketplace=marketplace, seller_id=seller_id))
            time.sleep(random.randint(4, 7))
            items = self.driver.find_elements_by_xpath("//*[@id=\"search\"]/div[1]/div[2]/div/span[4]/div[1]/div")
            ASINs = []
            for item in items[0:-1]:
                ASINs.append(item.get_attribute('data-asin'))

            logger.info(ASINs)
            listing_base = 'https://www.amazon.{marketplace}/dp/'.format(marketplace=marketplace)

            self.driver.execute_script("window.open('');")
            for ASIN in ASINs:
                logger.info(ASIN)
                record_flag = 0
                time.sleep(random.randint(5, 10))

                # Switch to the new window
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(random.randint(5, 10))
                logger.info(listing_base + ASIN)
                self.driver.get(listing_base + ASIN)
                time.sleep(random.randint(5, 10))
                if self.driver.page_source.find('Fulfilled by Amazon') < 0:
                    logger.info('ASIN: ' + ASIN + ' is not FBA')
                    continue
                title = self.driver.find_element_by_id('productTitle').text
                brand = self.driver.find_element_by_id('bylineInfo').text

                wrap_image = self.driver.find_element_by_id('landingImage').get_attribute('src')
                logger.info(wrap_image)
                rating = self.driver.find_element_by_id('acrCustomerReviewText').text
                try:
                    information = self.driver.find_element_by_id('prodDetails').text
                except Exception as e:
                    try:
                        information = self.driver.find_element_by_id('detail-bullets').text
                    except Exception as e:
                        try:
                            information = self.driver.find_element_by_id('detail_bullets_id').text
                        except Exception as e:
                            try:
                                information = self.driver.find_element_by_id('detailBullets_feature_div').text
                            except Exception as e:
                                self.save_page(traceback.format_exc())
                                print(e)
                logger.info(information)
                rank = ' '
                try:
                    rank_list = re.findall(r'Best Sellers Rank #(.*?)\(See Top 100 in', information)
                    logger.info(type(rank_list))
                    logger.info(rank_list)
                    rank = rank_list[0].lstrip('#')
                except Exception as e:
                    print(e)
                logger.info("rank: " + rank)

                shipping_weight_list = re.findall(r'Shipping Weight(.*?)\n', information)
                logger.info(type(shipping_weight_list))
                logger.info(shipping_weight_list)
                shipping_weight_str = shipping_weight_list[0]
                shipping_weight_num = shipping_weight_str.split(' ')[1]
                shipping_weight_dim = shipping_weight_str.split(' ')[2]
                logger.info(shipping_weight_num)
                logger.info(shipping_weight_dim)
                if shipping_weight_dim == 'pounds':
                    shipping_weight = shipping_weight_num
                elif shipping_weight_dim == 'g':
                    shipping_weight = str(float(shipping_weight_num) / 453.6)
                elif shipping_weight_dim == 'ounces':
                    shipping_weight = str(float(shipping_weight_num) / 16)
                logger.info("shipping_weight: " + shipping_weight)

                reviews_base = 'https://www.amazon.{marketplace}/product-reviews/'.format(marketplace=marketplace)
                logger.info(reviews_base + ASIN)
                self.driver.get(reviews_base + ASIN)
                star_rating = self.driver.find_element_by_xpath(
                    '//*[@id="cm_cr-product_info"]/div/div[1]/div[2]/div/div/div[2]/div/span').text

                logger.info("title: " + title)
                logger.info("brand: " + brand)
                logger.info("ratings: " + rating)
                logger.info("star: " + star_rating)
                today = datetime.date.today().strftime("%Y-%m-%d")
                url = "{seller_profit_domain}/product/update-info".format(seller_profit_domain=seller_profit_domain)
                sales_ranks_url = "{seller_profit_domain}/product/update-sales-rank".format(seller_profit_domain=seller_profit_domain)
                params = {"asin": ASIN, "sales_ranks": rank, "brand": brand, "small_image": wrap_image, "weight": shipping_weight}
                sales_ranks_params = {"asin": ASIN, "sales_ranks": rank, "date": today, "rating": rating}

                res = requests.post(url=url, data=params)
                logger.info(res)

                res = requests.post(url=sales_ranks_url, data=sales_ranks_params)
                logger.info(res)
                time.sleep(random.randint(5, 10))

        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)

    def review_info_scrapy(self, marketplace, seller_id, seller_profit_domain):
        try:
            self.driver.get(
                "https://www.amazon.{marketplace}/s?me={seller_id}&marketplaceID=ATVPDKIKX0DER".format(marketplace=marketplace, seller_id=seller_id))
            logger.info("https://www.amazon.{marketplace}/s?me={seller_id}&marketplaceID=ATVPDKIKX0DER".format(marketplace=marketplace, seller_id=seller_id))
            time.sleep(random.randint(1, 4))
            try:
                items = self.driver.find_elements_by_xpath("//*[@id=\"search\"]/div[1]/div[1]/div/span[4]/div[1]/div")
                if len(items) == 0:
                    items = self.driver.find_elements_by_xpath(
                        "//*[@id=\"search\"]/div[1]/div[2]/div/span[4]/div[1]/div")
            except Exception as e:
                print(e)

            ASINs = []
            for item in items[0:-1]:
                ASINs.append(item.get_attribute('data-asin'))

            logger.info(ASINs)
            listing_base = 'https://www.amazon.{marketplace}/dp/'.format(marketplace=marketplace)
            reviews_base = 'https://www.amazon.{marketplace}/product-reviews/'.format(marketplace=marketplace)

            for ASIN in ASINs:
                try:
                    logger.info('current asin is: ' + ASIN)
                    try:
                        if self.check_asin(ASIN):
                            return
                    except Exception as e:
                        print(e)
                    window_handles = self.driver.window_handles
                    logger.info('current window handles number is: ' + str(len(window_handles)))
                    if len(window_handles) > 2:
                        for i in range(2, window_handles):
                            self.driver.switch_to.window(self.driver.window_handles[i])
                            self.driver.close()
                            time.sleep(random.randint(1, 5))

                    if len(window_handles) == 0:
                        logger.info("open a new window")
                        self.driver.execute_script("window.open('');")
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    if len(window_handles) == 1:
                        self.driver.execute_script("window.open('');")
                        self.driver.switch_to.window(self.driver.window_handles[1])
                    if len(window_handles) == 2:
                        self.driver.switch_to.window(self.driver.window_handles[1])

                    time.sleep(random.randint(1, 5))


                    self.driver.get(listing_base + ASIN)
                    time.sleep(random.randint(1, 5))
                    if self.driver.page_source.find('Fulfilled by Amazon') < 0:
                        logger.info('ASIN: ' + ASIN + ' is not FBA')
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        continue

                    logger.info(reviews_base + ASIN)
                    self.driver.get(reviews_base + ASIN)
                    time.sleep(random.randint(5, 10))
                    review_rating_text = self.driver.find_element_by_xpath('//*[@id="cm_cr-product_info"]/div/div[1]/div[2]/div/div/div[2]/div/span').text.strip()
                    logger.info(review_rating_text)
                    if review_rating_text[0] == '0':
                        logger.info('ASIN: ' + ASIN + ' is no review')
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        continue
                    date_flag = False
                    today = datetime.utcnow().date()

                    self.driver.find_element_by_xpath('//*[@id="a-autoid-4-announce"]').click()
                    self.driver.find_element_by_id('sort-order-dropdown_1').click()
                    time.sleep(random.randint(5, 10))
                    self.driver.refresh()
                    while True:
                        time.sleep(random.randint(10, 20))
                        try:
                            try:
                                page_not_found = self.driver.find_element_by_xpath('//*[@id="g"]/div/a/img').get_attribute(
                                    'alter')
                                if page_not_found[0] == 'S':
                                    continue
                            except Exception as e:
                                print(e)

                            soup = BeautifulSoup(self.driver.page_source, 'lxml')

                            review_list = soup.select('#cm_cr-review_list > div')

                            if len(review_list) < 3:
                                break
                            reviews = review_list[0:-1]
                            logger.info(len(reviews))

                            for review in reviews:
                                logger.info(type(review))
                                try:
                                    review_id = review.attrs['id']
                                    logger.info("review_id: " + review_id)
                                    if len(review_id) < 1:
                                        continue
                                    if review_id[0] != 'R':
                                        continue
                                except Exception as e:
                                    print(e)
                                    continue
                                review_link = 'https://www.amazon.{marketplace}/gp/customer-reviews/{review_id}'.format(
                                        marketplace=marketplace, review_id=review_id)
                                time.sleep(random.randint(5, 10))

                                review_date_info = review.find(attrs={'data-hook': 'review-date'}).text
                                us_index = review_date_info.find('United States')
                                ca_index = review_date_info.find('Canada')
                                uk_index = review_date_info.find('United Kingdom')
                                review_country = 'US'
                                if us_index > 0:
                                    review_country = 'US'
                                if ca_index > 0:
                                    review_country = 'CA'
                                if uk_index > 0:
                                    review_country = 'UK'
                                try:
                                    reviewer_name = review.find(attrs={'class': 'a-profile-name'}).text
                                except Exception as e:
                                    print(e)
                                logger.info("reviewer_name: " + reviewer_name)

                                star_rating = review.find(attrs={'class': 'a-icon-alt'}).text
                                logger.info("review_star: " + star_rating)
                                review_title = review.find('a', attrs={'data-hook': 'review-title'}).text.strip()
                                logger.info("review_title: " + review_title)

                                review_date_info_list = review_date_info.split(' ')

                                review_date_year = review_date_info_list[-1]

                                review_date_day = review_date_info_list[-2][:-1]

                                review_date_month = list(calendar.month_name).index(review_date_info_list[-3])

                                review_date = review_date_year + '-' + str(review_date_month) + '-' + review_date_day
                                logger.info("review_date: " + review_date)
                                try:
                                    if (today - datetime.date(int(review_date_year), int(review_date_month), int(review_date_day))).days > 5:
                                        self.add_asin(ASIN)
                                        self.driver.close()
                                        handles = self.driver.window_handles
                                        self.driver.switch_to_window(handles[0])
                                        date_flag = True
                                        break
                                except Exception as e:
                                    logger.info("date error")
                                    print(e)

                                review_text = review.find(attrs={'data-hook': 'review-body'}).text
                                try:
                                    review_text = review_text.split("Install Flash Player ")[-1].strip()
                                except Exception as e:
                                    print(e)
                                logger.info("review_text: " + review_text)
                                review_image = 'no'
                                try:
                                    review_image = review.find(attrs={'class': 'review-image-tile'}).attrs['src']
                                    logger.info(review_image)
                                except Exception as e:
                                    print(e)
                                review_video = 'no'
                                try:
                                    review_video = review.find('video').attrs['src']
                                    logger.info(review_video)

                                except Exception as e:
                                    print(e)

                                verified = '0'
                                try:
                                    if review.find(attrs={'class': 'a-size-mini a-color-state a-text-bold'}).text == 'Verified Purchase':
                                        verified = '1'
                                except Exception as e:
                                    print(e)
                                logger.info("verified: " + verified)

                                time.sleep(random.randint(5, 10))

                                data = {'asin': ASIN, 'review_id': review_id, 'title': review_title, 'profile_name': reviewer_name,
                                        'verified_purchase': verified, 'review_text': review_text, 'review_rating': star_rating,
                                        'review_date': review_date, 'image': review_image, 'video': review_video,
                                        'review_link': review_link, 'country': review_country, "review_exist": "1"}
                                # data = {'asin' : 'B07FB627NR', 'review_id' : 'RGEGRP1HC0MMD', 'title' : 'Excellent price for a LEGO-compatible product', 'author' : 'Dr. Dolly Garnecki', 'verified' : 'Verified Purchase', 'text' : 'This arrived right away. My son was thrilled. He used his own cash to purchase these which he wants to use to build a world map, and then later glue to a coffee table to have his own brick table. These are great for bricks building on top as well as below--works either way. They're sturdy. He tried to bend them to break them, and they had flexibility, but they're not brittle.', 'star_rating' : '5', 'date' : 'March 11, 2019', 'image' : 'src="https://images-na.ssl-images-amazon.com/images/I/81iwr4KCyxL._SY88.jpg"', 'video' : ' '}

                                logger.info("review_image: " + review_image)
                                logger.info("review_video: " + review_video)
                                res = requests.post('{seller_profit_domain}/review/info'.format(seller_profit_domain=seller_profit_domain), data=data)

                                logger.info(res.text)
                            logger.info('date out of range: ')
                            logger.info(date_flag)

                            if not date_flag:
                                try:
                                    js_click_next_page = "document.querySelector('#cm_cr-pagination_bar > ul > li.a-last > a').click();"
                                    self.driver.execute_script(js_click_next_page)
                                except Exception as e:
                                    print(e)
                                    self.add_asin(ASIN)
                                    break
                            else:
                                break

                        except Exception as e:
                            print(e)
                except Exception as e:
                    self.save_page(traceback.format_exc())
                    print(e)
            self.clear_asin()
            # self.driver.close()
        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()


    def scroll_down(self,):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def go_to_listings_download_page(self):
        try:
            # 移动鼠标到inventory
            for i in range(0, 3):
                click = 'false'
                try:
                    inventory = WebDriverWait(self.driver, 40, 0.5).until(
                        EC.presence_of_element_located((By.ID, 'sc-navtab-inventory')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(inventory).perform()
                    logger.info('go to inventory')


                    # click inventory reports

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-inventory"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-inventory"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name == 'Inventory Reports':
                            time.sleep(random.randint(7, 9))
                            js_click_inventory_reports = "document.querySelector('#sc-navtab-inventory > ul > li:nth-child({}) > a').click();".format(
                                i)
                            self.driver.execute_script(js_click_inventory_reports)
                            logger.info('click inventory reports')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break
                except Exception as e:
                    print(e)

            # click Report Type drop down

            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'a-autoid-0-announce'))).click()

            logger.info('click Report Type drop down')
            time.sleep(random.randint(4, 7))

            # click all listing report

            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'dropdown1_7'))).click()

            logger.info('click all listing report')
            time.sleep(random.randint(4, 7))

            # click request report button

            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="a-autoid-5"]/span/input'))).click()

            logger.info('click request report button')
            time.sleep(random.randint(4, 7))

            self.driver.refresh()

            # download
            current_url = self.driver.current_url

            # 匹配“report_reference_id=”后面的数字
            pattern = re.compile(r'(?<=report_reference_id=)\d+\.?\d*')
            id = pattern.findall(current_url)[0]
            time.sleep(random.randint(1, 6))
            self.driver.refresh()
            for i in range(0, 3):
                try:
                    logger.info('%s-report_download' % id)
                    download_button = WebDriverWait(self.driver, 900, 0.5).until(EC.presence_of_element_located((By.ID, '%s-report_download' % id)))
                    download_button.click()
                    logger.info(download_button)
                    break
                except Exception as e:
                    print(e)
                    self.driver.quit()
            logger.info('All+Listings+Report+' + datetime.utcnow().date().strftime("%m-%d-%Y") + ".txt")
            time.sleep(random.randint(20, 50))
            return 'All+Listings+Report+' + datetime.utcnow().date().strftime("%m-%d-%Y") + ".txt"
        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()
    def close_tooltips(self):
        # close tooltips
        try:
            self.driver.find_element_by_xpath('//*[@id="step-0"]/div[2]/button').click()
        except:
            pass


    def multi_download(self):
        # close tooltips
        try:
            self.driver.find_element_by_xpath('//*[@id="step-0"]/div[2]/button').click()
        except:
            pass

    def go_to_today_orders_download_page(self):
        try:
            # 移动鼠标到reports
            for i in range(0, 3):
                click = 'false'
                try:
                    reports = WebDriverWait(self.driver, 20, 0.5).until(
                        EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                    logger.info('go to reports')

                    # click fulfillments

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        logger.info(report_name)
                        if report_name.startswith('Fulfil'):
                            time.sleep(random.randint(3, 7))
                            js_click_fulfillments = "document.querySelector('#sc-navtab-reports > ul > li:nth-child({}) > a').click();".format(
                                i)
                            self.driver.execute_script(js_click_fulfillments)
                            logger.info('click fulfillments')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break
                except Exception as e:
                    print(e)

            # click all orders

            try:
                WebDriverWait(self.driver, 20, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-sidepanel"]/div/ul[3]/li[10]/a'))).click()
                time.sleep(random.randint(1, 7))
            except Exception as e:
                print(e)

            js_click_all_orders = "document.querySelector('#FlatFileAllOrdersReport > a').click();"
            self.driver.execute_script(js_click_all_orders)

            logger.info('click all orders')
            time.sleep(random.randint(1, 7))

            # click order date drop down

            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'eventDateType'))).click()

            time.sleep(random.randint(1, 7))

            # select Last Updated Date

            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="eventDateType"]/select/option[2]'))).click()

            logger.info('choose Last Updated Date')
            time.sleep(random.randint(1, 7))

            # click last date drop down

            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.ID, 'downloadDateDropdown'))).click()

            time.sleep(random.randint(1, 7))

            # select Exact Date

            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadDateDropdown"]/option[6]'))).click()

            time.sleep(random.randint(1, 7))

            # From today to today

            from_elem = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#fromDateDownload')))
            # today = datetime.datetime.today().strftime("%m/%d/%Y")
            today = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-7))).strftime("%m/%d/%Y")
            time.sleep(random.randint(1, 7))
            for i in range(0, 30):
                from_elem.send_keys('\b')
            from_elem.send_keys(today)
            logger.info(from_elem.get_attribute('value'))
            time.sleep(random.randint(3, 7))
            to_elem = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#toDateDownload')))
            for i in range(0, 30):
                to_elem.send_keys('\b')
            time.sleep(random.randint(1, 7))
            to_elem.send_keys(today)

            logger.info('select today')
            time.sleep(random.randint(4, 7))

            # click download

            WebDriverWait(self.driver, 120, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="requestDownload"]/td[2]/button'))).click()

            logger.info('download request')
            time.sleep(random.randint(1, 7))

            WebDriverWait(self.driver, 900, 0.5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a/span/span'))).click()
            logger.info('downloading')
            time.sleep(random.randint(20, 50))
            download_button = self.driver.find_element_by_xpath('//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a')
            # download_button = WebDriverWait(self.driver, 40, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a')))
            logger.info("download_button")

            download_link = download_button.get_attribute("href")

            logger.info(download_link)
            orders_name = re.findall(r"GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE__(\d*)\.txt", download_link)[0]
            logger.info(orders_name)
            return orders_name + '.txt'

        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()


    def go_to_orders_download_page(self):
        try:
            # 移动鼠标到reports
            for i in range(0, 3):
                click = 'false'
                try:
                    reports = WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                    logger.info('go to reports')

                    # click fulfillments

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name.startswith('Fulfil'):
                            time.sleep(random.randint(3, 7))
                            js_click_fulfillments = "document.querySelector('#sc-navtab-reports > ul > li:nth-child({}) > a').click();".format(i)
                            self.driver.execute_script(js_click_fulfillments)
                            logger.info('click fulfillments')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break

                except Exception as e:
                    print(e)

            # click all orders
            try:
                WebDriverWait(self.driver, 20, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-sidepanel"]/div/ul[3]/li[10]/a'))).click()
                time.sleep(random.randint(1, 7))
            except Exception as e:
                print(e)

            js_click_all_orders = "document.querySelector('#FlatFileAllOrdersReport > a').click();"
            self.driver.execute_script(js_click_all_orders)

            logger.info('click all orders')
            time.sleep(random.randint(1, 7))

            # click order date drop down

            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'eventDateType'))).click()

            time.sleep(random.randint(1, 7))

            # select Last Updated Date

            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="eventDateType"]/select/option[2]'))).click()

            logger.info('choose Last Updated Date')
            time.sleep(random.randint(1, 7))

            # click last date drop down

            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'downloadDateDropdown'))).click()

            time.sleep(random.randint(1, 7))

            # select Last Updated Date

            pt = '//*[@id="downloadDateDropdown"]/option[{}]'.format(random.randint(2, 3))
            logger.info(pt)
            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.XPATH, pt))).click()

            logger.info('choose 3/7 Date')
            time.sleep(random.randint(1, 7))

            # click download

            WebDriverWait(self.driver, 120, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requestDownload"]/td[2]/button'))).click()

            logger.info('download request')
            time.sleep(random.randint(1, 7))

            WebDriverWait(self.driver, 900, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a/span/span'))).click()
            logger.info('downloading')
            time.sleep(random.randint(20, 50))
            download_button = self.driver.find_element_by_xpath('//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a')
            # download_button = WebDriverWait(self.driver, 40, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a')))
            logger.info("download_button")

            download_link = download_button.get_attribute("href")

            logger.info(download_link)
            orders_name = re.findall(r"GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE__(\d*)\.txt", download_link)[0]
            logger.info(orders_name)
            return orders_name + '.txt'
        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()


    def go_to_FBA_shipment_download_page(self):

        try:
            # 移动鼠标到reports
            for i in range(0, 3):
                click = 'false'
                try:
                    reports = WebDriverWait(self.driver, 940, 0.5).until(
                        EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                    logger.info('go to reports')

                    # click fulfillments

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name.startswith('Fulfil'):
                            time.sleep(random.randint(7, 9))
                            js_click_fulfillments = "document.querySelector('#sc-navtab-reports > ul > li:nth-child({}) > a').click();".format(
                                i)
                            self.driver.execute_script(js_click_fulfillments)
                            logger.info('click fulfillments')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break
                except Exception as e:
                    print(e)

            # click Amazon Fulfilled Shipments

            WebDriverWait(self.driver, 940, 0.5).until(EC.presence_of_element_located((By.ID, 'AFNShipmentReport'))).click()

            logger.info('click Amazon Fulfilled Shipments')
            time.sleep(random.randint(1, 7))

            # click event date drop down

            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.ID, 'downloadDateDropdown'))).click()

            logger.info('click event date drop down')
            time.sleep(random.randint(1, 7))

            # choose date range

            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#downloadDateDropdown > option:nth-child({})'.format(random.randint(3, 5))))).click()

            logger.info('date range')
            time.sleep(random.randint(1, 7))

            # click  Request .txt Download

            WebDriverWait(self.driver, 960, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requestCsvTsvDownload"]/tr[1]/td[3]/button'))).click()

            logger.info('click  Request .txt Download')
            time.sleep(random.randint(1, 7))
            # click download

            download_button = WebDriverWait(self.driver, 900, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[5]/a')))
            download_button.click()

            logger.info('downloading')
            time.sleep(random.randint(20, 50))

            download_link = download_button.get_attribute("href")
            logger.info(download_link)
            FBA_shippment_name = re.findall(r"GET_AMAZON_FULFILLED_SHIPMENTS_DATA__(\d*)\.txt", download_link)[0]
            logger.info(FBA_shippment_name)
            return FBA_shippment_name + '.txt'

        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()

    def go_to_finance_download_page(self):
        try:
            # 移动鼠标到reports
            for i in range(0, 8):
                click = 'false'
                try:
                    reports = WebDriverWait(self.driver, 940, 0.5).until(
                        EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                    logger.info('go to reports')

                    # click payments

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name == 'Payments':
                            time.sleep(random.randint(3, 7))
                            js_click_payments = "document.querySelector('#sc-navtab-reports > ul > li:nth-child({}) > a').click();".format(
                                i)
                            self.driver.execute_script(js_click_payments)
                            logger.info('click payments')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break

                except Exception as e:
                    print(e)


            # click data range report

            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#PaymentTabs > div > ul > li:nth-child(4)'))).click()

            logger.info('click data range report')
            time.sleep(random.randint(4, 7))

            # click generate report

            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrGenerateReportButton'))).click()

            logger.info('click data range report')
            time.sleep(random.randint(4, 7))

            # select date

            start = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrFromDate')))
            start.click()
            seven_days_ago = (datetime.utcnow().date() - timedelta(days=random.randint(7, 10))).strftime("%m/%d/%Y")
            start.send_keys(seven_days_ago)
            time.sleep(random.randint(3, 7))
            end = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrToDate')))
            end.click()
            yesterday = (datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-7))) - timedelta(days=1)).strftime("%m/%d/%Y")
            end.send_keys(yesterday)

            logger.info('select date')
            time.sleep(random.randint(4, 7))

            # generate

            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrGenerateReportsGenerateButton'))).click()

            logger.info('select date')
            time.sleep(random.randint(10, 20))
            self.scroll_down()
            self.driver.refresh()
            time.sleep(random.randint(20, 30))
            # click download

            download_button = WebDriverWait(self.driver, 900, 0.5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="downloadButton"]/span/a')))
            download_button.click()
            logger.info('click download')
            time.sleep(random.randint(4, 7))
            download_link = download_button.get_attribute("href")
            bulk_report = re.findall(r"fileName=(.*)?\.csv", download_link)[0]
            logger.info(bulk_report)
            time.sleep(random.randint(10, 20))
            return bulk_report + '.csv'
        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()


    def go_to_FBA_inventory_download_page(self):
        try:
            # 移动鼠标到reports
            for i in range(0, 3):
                click = 'false'
                try:
                    reports = WebDriverWait(self.driver, 940, 0.5).until(
                        EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                    logger.info('go to reports')

                    # click fulfillments

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name.startswith('Fulfil'):
                            time.sleep(random.randint(3, 7))
                            js_click_fulfillments = "document.querySelector('#sc-navtab-reports > ul > li:nth-child({}) > a').click();".format(
                                i)
                            self.driver.execute_script(js_click_fulfillments)
                            logger.info('click fulfillments')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break
                except Exception as e:
                    print(e)


            # click inventory show more
            try:
                WebDriverWait(self.driver, 910, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#sc-sidepanel > div > ul:nth-child(3) > li.level3-header.show-more > a'))).click()
            except Exception as e:
                print(e)
                try:
                    WebDriverWait(self.driver, 910, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#sc-sidepanel > div > ul:nth-child(3) > li.level3-header.show-more > a'))).click()
                except Exception as e:
                    print(e)
            logger.info('click inventory show more')
            time.sleep(random.randint(4, 7))

            # click Manage FBA Inventory

            reports = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.ID, 'FBA_MYI_UNSUPPRESSED_INVENTORY')))
            time.sleep(random.randint(4, 7))
            webdriver.ActionChains(self.driver).move_to_element(reports).perform()
            reports.click()
            logger.info('click Manage FBA Inventory')
            time.sleep(random.randint(5, 9))


            # click Request .txt Download

            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="requestCsvTsvDownload"]/tr[1]/td[3]/button'))).click()

            logger.info('Request .txt Download')
            time.sleep(random.randint(20, 40))

            # click download

            download_button = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr/td[5]/a')))
            download_button.click()

            logger.info('downloading')
            time.sleep(random.randint(20, 50))


            download_link = download_button.get_attribute("href")
            logger.info(download_link)
            FBA_inventory = re.findall(r"_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA__(\d*)\.txt", download_link)[0]
            logger.info(FBA_inventory)
            return FBA_inventory + '.txt'
        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()


    def go_to_advertising_reports_download_page(self):
        try:
            # 移动鼠标到reports
            for i in range(0, 3):
                click = 'false'
                try:
                    reports = WebDriverWait(self.driver, 940, 0.5).until(
                        EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                    logger.info('go to reports')

                    # click advertising reports

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name == 'Advertising Reports':
                            time.sleep(random.randint(5, 9))
                            js_click_advertising_reports = "document.querySelector('#sc-navtab-reports > ul > li:nth-child({}) > a').click();".format(
                                i)
                            self.driver.execute_script(js_click_advertising_reports)
                            logger.info('click advertising reports')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break
                except Exception as e:
                    print(e)


            # choose Advertised product

            # click drop down
            try:
                WebDriverWait(self.driver, 940, 0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="advertising-reports"]/div/div/div/div[1]/a/button')))
                create_report = "document.querySelector('#advertising-reports > div > div > div > div.sc-VigVT.dzhatw > a').click()"
                self.driver.execute_script(create_report)
            except Exception as e:
                WebDriverWait(self.driver, 940, 0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="advertising-reports"]/div/div/div/div[1]/a')))
                create_report = "document.querySelector('#advertising-reports > div > div > div > div.sc-VigVT.iBsGPR > a').click()"
                self.driver.execute_script(create_report)
            time.sleep(random.randint(4, 7))
            # advertised_product_drop_down = "document.querySelector('#cards-container > div.sc-chPdSV.iiDyb > div > div.sc-1xc1ftl-1.evvFrQ > table > tbody > tr:nth-child(2) > td > label > button > span').click()"
            advertised_product_drop_down = "document.querySelector('#cards-container > div.sc-chPdSV.hJxqxz > div > div.sc-1xc1ftl-1.evvFrQ > table > tbody > tr:nth-child(2) > td > label > button > span').click()"
            self.driver.execute_script(advertised_product_drop_down)
            time.sleep(random.randint(4, 7))
            choose_advertised_product = "document.querySelector('#portal > div > div > button:nth-child(3)').click()"

            self.driver.execute_script(choose_advertised_product)
            time.sleep(random.randint(4, 7))

            # click daily
            # data_unit_drop_down = "document.querySelector('#tresah > div > div > div.a-container.sspa-bottomless > div:nth-child(4) > section > div.tresah-form-center > div.tresah-inputs-right > div:nth-child(2) > span > span > span > span').click()"
            # self.driver.execute_script(data_unit_drop_down)
            choose_daily = "document.querySelector('#undefined-day').click()"
            self.driver.execute_script(choose_daily)

            logger.info('choose Advertised product')
            time.sleep(random.randint(4, 7))

            # select date

            # click drop down

            report_period = "document.querySelector('#cards-container > div.sc-chPdSV.hJxqxz > div > div.sc-1xc1ftl-1.evvFrQ > table > tbody > tr:nth-child(4) > td > button').click()"
            self.driver.execute_script(report_period)
            time.sleep(random.randint(4, 7))

            js = "document.querySelector('#portal > div > div > div > div.sc-11mc28f-3.jWiMFK > button:nth-child(%s)').click();" % random.randint(1, 5)
            logger.info(js)
            self.driver.execute_script(js)
            logger.info('click drop down')

            time.sleep(random.randint(4, 7))

            logger.info('select date')
            time.sleep(random.randint(4, 7))

            # click create report

            create_report = "document.querySelector('#run-report-button').click()"
            self.driver.execute_script(create_report)

            logger.info('click create report')
            time.sleep(random.randint(10, 20))

            # click download
            # 移动鼠标到reports
            for i in range(0, 3):
                click = 'false'
                try:
                    reports = WebDriverWait(self.driver, 940, 0.5).until(
                        EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                    time.sleep(random.randint(4, 7))
                    webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                    logger.info('go to reports')

                    # click advertising reports

                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name == 'Advertising Reports':
                            time.sleep(random.randint(5, 9))
                            js_click_advertising_reports = "document.querySelector('#sc-navtab-reports > ul > li:nth-child({}) > a').click();".format(
                                i)
                            self.driver.execute_script(js_click_advertising_reports)
                            logger.info('click advertising reports')
                            time.sleep(random.randint(1, 7))
                            click = 'true'
                            break
                    if click == 'true':
                        break
                except Exception as e:
                    print(e)

            # click download reports

            for i in range(30):
                report_status = self.driver.find_element_by_xpath('//*[@id="advertising-reports"]/div/div/div/div[2]/div[1]/div[2]/div[1]/div/div[1]/div/div/p').text
                logger.info(report_status)
                if report_status == "Completed":
                    break
                else:
                    self.driver.refresh()
                    time.sleep(random.randint(10, 15))
            js_click_download = "document.querySelector('#advertising-reports > div > div > div > div.ReactTable > div.rt-table > div.rt-tbody > div:nth-child(1) > div > div:nth-child(2) > span > a').click();"
            self.driver.execute_script(js_click_download)
            logger.info('click download')
            time.sleep(random.randint(4, 7))


            dir_list = os.listdir(os.path.expanduser('~/Downloads/'))
            dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(os.path.expanduser('~/Downloads/'), x)))
            return dir_list[-1]
            # return 'Sponsored Products Search term report.xlsx'

        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()

    def go_to_advertising_search_term_reports_download_page(self):

        # 移动鼠标到reports
        for i in range(0, 3):

            try:
                reports = WebDriverWait(self.driver, 940, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(5, 9))
            except Exception as e:
                print(e)

            # click advertising reports
            try:
                js_click_advertising_reports = "document.querySelector('#sc-navtab-reports > ul > li:nth-child(6) > a').click();"
                self.driver.execute_script(js_click_advertising_reports)
                logger.info('click advertising reports')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)

        # choose daily
        try:
            # click drop down
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[2]/div[2]/div[2]/span/span'))).click()
            time.sleep(random.randint(4, 7))

            # click daily
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dropdown1_1"]'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('choose daily')
        time.sleep(random.randint(4, 7))

        # select week to date
        try:

            # select week to date
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[2]/div[2]/div[1]/div/div/span/span/span'))).click()
            time.sleep(random.randint(4, 7))

            js = "document.querySelector('#a-popover-2 > div > div > ul > li:nth-child(3) > a').click();"
            self.driver.execute_script(js)
            logger.info('select week to date')


            time.sleep(random.randint(4, 7))
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('select date')
        time.sleep(random.randint(4, 7))

        # click create report
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[1]/span/span/input'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click create report')
        time.sleep(random.randint(30, 60))

        # click download
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[3]/div/div/div/div[2]/div/div[5]/span/span/a'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click download')
        time.sleep(random.randint(20, 30))

        dir_list = os.listdir(os.path.expanduser('~/Downloads/'))
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(os.path.expanduser('~/Downloads/'), x)))
        return dir_list[-1]

        # return 'Sponsored Products Search term report.xlsx'

    def go_to_campaigns_bulk_report_download(self):

        # 移动鼠标到reports
        for i in range(0, 3):
            try:
                reports = WebDriverWait(self.driver, 940, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(5, 9))
            except Exception as e:
                print(e)

            # click advertising reports
            try:
                js_click_advertising_reports = "document.querySelector('#sc-navtab-reports > ul > li:nth-child(6) > a').click();"
                self.driver.execute_script(js_click_advertising_reports)
                logger.info('click advertising reports')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # click bulk operations
        try:
            WebDriverWait(self.driver, 900, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[1]/nav/ul/a[3]'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click bulk operations')
        time.sleep(random.randint(4, 7))

        # click create spreadsheet for download
        try:
            WebDriverWait(self.driver, 900, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="request-entity-report-submit"]/span/input'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click create spreadsheet for download')
        time.sleep(random.randint(4, 7))
        self.scroll_down()

        # click download
        while True:
            try:
                self.driver.refresh()
                time.sleep(random.randint(10, 25))
                try:
                    download_button = WebDriverWait(self.driver, 900, 0.5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="downloadHistoryId"]/tbody/tr[2]/td[2]/div/a')))
                    download_button.click()
                    logger.info('click download')
                    time.sleep(random.randint(20, 50))

                    # sort by get time return the latest one

                    dir_list = os.listdir(os.path.expanduser('~/Downloads/'))
                    dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(os.path.expanduser('~/Downloads/'), x)))
                    return dir_list[-1]
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)

    def go_to_business_report_download(self):

        # 移动鼠标到reports
        for i in range(0, 3):
            try:
                reports = WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(5, 9))
            except Exception as e:
                print(e)

            # click business reports
            try:
                js_click_business_reports = "document.querySelector('#sc-navtab-reports > ul > li:nth-child(4) > a').click();"
                self.driver.execute_script(js_click_business_reports)
                logger.info('click business reports')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # click detail page sales and traffic
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="report_DetailSalesTrafficBySKU"]'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click detail page sales and traffic')
        time.sleep(random.randint(4, 7))

        # click download drop down
        try:
            WebDriverWait(self.driver, 900, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="export"]/div'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click download drop down')
        time.sleep(random.randint(4, 7))

        # choose csv
        try:
            WebDriverWait(self.driver, 900, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadCSV"]'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('choose csv')
        try:
            time.sleep(random.randint(10, 50))
            year = str(int(datetime.date.today().strftime('%y')))
            month = str(int(datetime.date.today().strftime('%m')))
            day = str(int(datetime.date.today().strftime('%d')))
            file_name = 'BusinessReport-' + month + '-' + day + '-' + year + '.csv'
            logger.info(file_name)
        except Exception as e:
            print(e)
            self.driver.quit()
        return file_name

    def upload_files(self, url, file_name, email, password, seller_id, file_type, country, seller_profit_domain):
        try:

            rootdir = os.path.expanduser('~/Downloads/')
            logger.info(rootdir)
            file_path = rootdir + file_name
            logger.info(file_path)
            logger.info("gideon login")

            js = 'window.open("{seller_profit_domain}/login");'.format(seller_profit_domain=seller_profit_domain)
            self.driver.execute_script(js)

            handles = self.driver.window_handles
            self.driver.switch_to_window(handles[1])
            try:
                email_input_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['email'])))
                email_input_elem.clear()
                email_input_elem.send_keys(email)
                logger.info("put password")
                password_input_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['password'])))
                password_input_elem.clear()
                password_input_elem.send_keys(password)
                login_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['login'])))
                login_elem.click()
            except Exception as e:
                print(e)

            time.sleep(4)

            logger.info("upload file to gideon")
            self.driver.get(url)

            if file_type == "orders_file":

                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['order_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )

                logger.info("file_upload")
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['orders_import']))).click()

            if file_type == "order_shipments_file":

                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['FBA_shipments_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)

                self.scroll_down()
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['FBA_shipments_import']))).click()

            if file_type == "finances_file":

                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['finance_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("select country")
                country_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['finance_country'])))
                Select(country_elem).select_by_value(country)

                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['finance_import']))).click()

            if file_type == "ads_file":

                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['ads_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("select country")
                country_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['ads_country'])))
                Select(country_elem).select_by_value(country)

                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['ads_import']))).click()

            if file_type == "campaigns_file":

                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['campaigns_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("select country")
                country_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['campaigns_country'])))
                Select(country_elem).select_by_value(country)

                logger.info("select report date")
                date_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['campaigns_date'])))
                date_elem.value = (datetime.utcnow().date() - timedelta(days=1)).strftime("%Y-%m-%d")
                logger.info(date_elem.value)
                time.sleep(5)
                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['campaigns_import']))).click()

            if file_type == "searchterms_file":

                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['searchterms_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("select country")
                country_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['searchterms_country'])))
                Select(country_elem).select_by_value(country)

                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                self.scroll_down()
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['searchterms_import']))).click()

            if file_type == "listings_file":

                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['listings_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("select country")
                country_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['listings_country'])))
                Select(country_elem).select_by_value(country)

                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['listings_import']))).click()

            if file_type == "inventory_file":
                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['FBA_inventory_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("select country")
                country_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['FBA_inventory_country'])))
                Select(country_elem).select_by_value(country)

                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['FBA_inventory_import']))).click()

            if file_type == "business_file":
                logger.info("select seller")
                seller_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['business_seller_selector'])))
                Select(seller_elem).select_by_value(seller_id)

                logger.info("select report date")
                date_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['business_date'])))
                date_elem.value = datetime.utcnow().date().strftime("%Y-%m-%d")

                logger.info("select country")
                country_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['business_country'])))
                Select(country_elem).select_by_value(country)

                logger.info("file_upload")
                file_upload = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, file_type))
                )
                file_upload.send_keys(file_path)
                time.sleep(random.randint(1, 5))

                logger.info("file import")
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['business_import']))).click()


            time.sleep(random.randint(20, 30))
            self.driver.close()
            self.driver.switch_to_window(handles[0])
            os.remove(file_path)
        except Exception as e:
            self.save_page(traceback.format_exc())
            print(e)
            self.driver.quit()

    def close_webdriver(self):
        self.driver.quit()

    def save_page(self, ex):
        try:
            logger.info('begin to save page')
            file_name = time.strftime("%b_%d_%a_%H_%M_%S", time.localtime()) + '.html'
            current_path = os.getcwd()
            file_path = current_path + '\\logs\\' + file_name

            if not os.path.exists(current_path + '\\logs\\'):
                os.makedirs(current_path + '\\logs\\')
            f = open(file_path, 'w', encoding='utf-8')
            f.write(self.driver.page_source)
            f.close()

            log_path = current_path + '\\logs\\' + 'log.txt'

            f = open(log_path, 'a', encoding='utf-8')
            f.write(ex)
            f.write(time.strftime("%b %d %a %H:%M:%S", time.localtime()) + '----------------------------------------------------------------' + '\n')
            f.close()
            logger.info('page save done')
            time.sleep(random.randint(5, 10))
        except Exception as e:
            print(e)

    def add_asin(self, asin):
        try:
            logger.info('begin to add asin')
            current_path = os.getcwd()
            file_path = current_path + '\\' + 'asin.txt'
            f = open(file_path, 'a', encoding='utf-8')
            f.write(asin + '\n')
            f.close()
            logger.info('asin' + ' ' + asin + ' ' + 'save done')
            time.sleep(random.randint(5, 10))
        except Exception as e:
            print(e)

    def check_asin(self, asin):
        try:
            current_path = os.getcwd()
            file_path = current_path + '\\' + 'asin.txt'
            f = open(file_path, 'r', encoding='utf-8')
            for asin_done in f:
                if asin == asin_done.strip():
                    logger.info('asin' + ' ' + asin + ' ' + 'is done')
                    return True
            f.close()
            logger.info('asin' + ' ' + asin + ' ' + 'is not done yet')
            return False
        except Exception as e:
            print(e)

    def clear_asin(self):
        try:
            current_path = os.getcwd()
            file_path = current_path + '\\' + 'asin.txt'
            f = open(file_path, 'r+', encoding='utf-8')
            f.truncate()
            f.close()
            self.add_asin('asin')
            logger.info('clear asins')
            return False
        except Exception as e:
            print(e)



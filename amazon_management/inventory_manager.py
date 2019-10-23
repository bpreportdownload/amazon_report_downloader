import time
import random
import re
import os
import datetime
import calendar
import urllib.request
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.base import BaseTrigger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException)

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium import webdriver
from amazon_management import logger


class InventoryManager(object):
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
            'password': '#password',
            'email': '#email',
            'login': 'body > div.container-fluid > div > div > div > div > div > div > div.panel-body > form > div:nth-child(5) > div > button',
            'orders_file': '#orders_file'
        }

    def get_total_products_cnt(self):
        total_products_cnt = 0
        total_products_str = ''
        while True:
            try:
                total_products_elem = WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['total_products_selector'])))
                total_products_str = total_products_elem.get_attribute('innerText')
                total_products_cnt = int(total_products_str.replace(',', ''))
                break
            except StaleElementReferenceException:
                pass
            except (NoSuchElementException, TimeoutException):
                raise RuntimeError(
                    'Could not find total products element - %s' % self.selectors['total_products_selector'])
            except ValueError:
                raise RuntimeError('Could not parse total products text - %s' % total_products_str)

        return total_products_cnt

    def get_total_product_pages_cnt(self):
        total_product_pages_cnt = 0
        total_product_pages_str = ''
        while True:
            try:
                total_product_pages_elem = WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['total_product_pages_selector'])))
                total_product_pages_str = total_product_pages_elem.text
                total_product_pages_cnt = int(total_product_pages_str.split(' ').pop())
                break
            except StaleElementReferenceException:
                pass
            except (NoSuchElementException, TimeoutException):
                total_product_pages_cnt = 0
                break
            except ValueError:
                raise RuntimeError('Could not parse total product pages text - %s' % total_product_pages_str)
            except:
                raise RuntimeError(
                    'Could not find total product pages element - %s' % self.selectors['total_product_pages_selector'])

        return total_product_pages_cnt

    def go_to_page(self, page):
        while True:
            try:
                page_input_elem = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['page_input_selector'])))
                page_input_elem.clear()
                page_input_elem.send_keys(page)

                go_to_page_elem = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['go_to_page_selector'])))
                go_to_page_elem.click()

                break
            except StaleElementReferenceException:
                pass
            except:
                break

    def select_all(self):
        while True:
            try:
                select_all_elem = WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['select_all_selector'])))
                script = 'document.querySelector("{}").click()'.format(
                    self.selectors['select_all_selector'])
                self.driver.execute_script(script)
                break
            except StaleElementReferenceException as e:
                logger.exception(e)
            except WebDriverException as e:
                if e.msg.find('is not clickable') != -1:
                    logger.exception(e)
                    continue

                raise e
            except:
                raise RuntimeError(
                    'Could not find select all element - %s' % self.selectors['select_all_selector'])

    def scroll_down(self,):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def delete_selected(self):
        result = True

        while True:
            try:
                bulk_action_select_elem = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['bulk_action_select_selector'])))
                bulk_action_select = Select(bulk_action_select_elem)
                bulk_action_select.select_by_value('myitable-delete')
                break
            except StaleElementReferenceException:
                pass



        return result


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
            # 'general_import': '#page-content-wrapper > div:nth-child(3) > div > div:nth-child(1) > div > div > div.panel-body > form > div:nth-child(6) > div > button',
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



    def scroll_down(self,):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def go_to_listings_download_page(self):

        # 移动鼠标到inventory
        for i in range(0, 3):
            try:
                inventory = WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-inventory')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(inventory).perform()
                logger.info('go to inventory')
                time.sleep(random.randint(7, 9))
            except Exception as e:
                print(e)

            # click inventory reports
            try:
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-inventory"]/ul/li[7]/a'))).click()
                logger.info('click inventory reports')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # click Report Type drop down
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'a-autoid-0-announce'))).click()
        except Exception as e:
            print(e)
        logger.info('click Report Type drop down')
        time.sleep(random.randint(4, 7))

        # click all listing report
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'dropdown1_7'))).click()
        except Exception as e:
            print(e)
        logger.info('click all listing report')
        time.sleep(random.randint(4, 7))

        # click request report button
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="a-autoid-5"]/span/input'))).click()
        except Exception as e:
            print(e)
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
                download_button = WebDriverWait(self.driver, 40, 0.5).until(EC.presence_of_element_located((By.ID, '%s-report_download' % id)))
                download_button.click()
                logger.info(download_button)
                break
            except Exception as e:
                print(e)
        logger.info('All+Listings+Report+' + datetime.date.today().strftime("%m-%d-%Y") + ".txt")
        time.sleep(random.randint(1, 6))
        return 'All+Listings+Report+' + datetime.date.today().strftime("%m-%d-%Y") + ".txt"

    def close_tooltips(self):
        # close tooltips
        try:
            self.driver.find_element_by_xpath('//*[@id="step-0"]/div[2]/button').click()
        except:
            pass


    def go_to_orders_download_page(self):

        # 移动鼠标到reports
        for i in range(0, 3):
            try:
                reports = WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(7, 9))
            except Exception as e:
                print(e)

            # click fulfillments
            try:
                WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[5]/a'))).click()
                logger.info('click fulfillments')
                time.sleep(random.randint(1, 7))
                break
            except Exception as e:
                print(e)


        # click all orders
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'FlatFileAllOrdersReport'))).click()
        except Exception as e:
            print(e)
        logger.info('click all orders')
        time.sleep(random.randint(1, 7))

        # click order date drop down
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'eventDateType'))).click()
        except Exception as e:
            print(e)
        time.sleep(random.randint(1, 7))

        # select Last Updated Date
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="eventDateType"]/select/option[2]'))).click()
        except Exception as e:
            print(e)
        logger.info('choose Last Updated Date')
        time.sleep(random.randint(1, 7))

        # click download
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requestDownload"]/td[2]/button'))).click()
        except Exception as e:
            print(e)
        logger.info('download request')
        time.sleep(random.randint(1, 7))

        while True:
            try:
                WebDriverWait(self.driver, 40, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a/span/span'))).click()
                logger.info('downloading')
                time.sleep(random.randint(1, 7))
                download_button = self.driver.find_element_by_xpath('//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a')
                # download_button = WebDriverWait(self.driver, 40, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a')))
                logger.info("download_button")
                try:

                    download_link = download_button.get_attribute("href")

                    logger.info(download_link)
                    orders_name = re.findall(r"GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE__(\d*)\.txt", download_link)[0]
                    logger.info(orders_name)
                    return orders_name + '.txt'
                except Exception as e:
                    print(e)
            except StaleElementReferenceException:
                pass
            except (NoSuchElementException, TimeoutException):
                break
            except:
                raise RuntimeError(
                    'Could not find total product pages element - %s' % self.selectors['total_product_pages_selector'])

    def go_to_FBA_shipment_download_page(self):
        # 移动鼠标到reports
        for i in range(0, 3):
            try:
                reports = WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(7, 9))
            except Exception as e:
                print(e)

            # click fulfillments
            try:
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[5]/a'))).click()
                logger.info('click fulfillments')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # click Amazon Fulfilled Shipments
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'AFNShipmentReport'))).click()
        except Exception as e:
            print(e)
        logger.info('click Amazon Fulfilled Shipments')
        time.sleep(random.randint(1, 7))

        # click event date drop down
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'downloadDateDropdown'))).click()
        except Exception as e:
            print(e)
        logger.info('click event date drop down')
        time.sleep(random.randint(1, 7))

        # choose yesterday
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#downloadDateDropdown > option:nth-child(2)'))).click()
        except Exception as e:
            print(e)
        logger.info('choose yesterday')
        time.sleep(random.randint(1, 7))

        # click  Request .txt Download
        try:
            WebDriverWait(self.driver, 40, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requestCsvTsvDownload"]/tr[1]/td[3]/button'))).click()
        except Exception as e:
            print(e)
        logger.info('click  Request .txt Download')
        time.sleep(random.randint(1, 7))
        # click download
        try:
            download_button = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[5]/a')))
            download_button.click()
        except Exception as e:
            print(e)
        logger.info('downloading')
        time.sleep(random.randint(1, 7))

        try:
            download_link = download_button.get_attribute("href")
            logger.info(download_link)
            FBA_shippment_name = re.findall(r"GET_AMAZON_FULFILLED_SHIPMENTS_DATA__(\d*)\.txt", download_link)[0]
            logger.info(FBA_shippment_name)
            return FBA_shippment_name + '.txt'
        except Exception as e:
            print(e)


    def go_to_finance_download_page(self):

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

            # click payments
            try:
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[2]/a'))).click()
                logger.info('click payments')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # click data range report
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#PaymentTabs > div > ul > li:nth-child(4)'))).click()
        except Exception as e:
            print(e)
        logger.info('click data range report')
        time.sleep(random.randint(4, 7))

        # click generate report
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrGenerateReportButton'))).click()
        except Exception as e:
            print(e)
        logger.info('click data range report')
        time.sleep(random.randint(4, 7))

        # select date
        try:
            start = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrFromDate')))
            start.click()
            three_days_ago = (datetime.date.today() - datetime.timedelta(days=3)).strftime("%m/%d/%Y")
            start.send_keys(three_days_ago)
            end = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrToDate')))
            end.click()
            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")
            end.send_keys(yesterday)
        except Exception as e:
            print(e)
        logger.info('select date')
        time.sleep(random.randint(4, 7))

        # generate
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrGenerateReportsGenerateButton'))).click()
        except Exception as e:
            print(e)
        logger.info('select date')
        time.sleep(random.randint(30, 60))
        self.scroll_down()
        self.driver.refresh()
        time.sleep(random.randint(10, 20))
        # click download
        try:
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
            print(e)

    def go_to_FBA_inventory_download_page(self):

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

            # click fulfillments
            try:
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[5]/a'))).click()
                logger.info('click fulfillments')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # click inventory show more
        try:
            WebDriverWait(self.driver, 10, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="sc-sidepanel"]/div/ul[2]/li[23]/a'))).click()
        except Exception as e:
            print(e)
            try:
                WebDriverWait(self.driver, 10, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-sidepanel"]/div/ul[2]/li[21]/a'))).click()
            except Exception as e:
                print(e)
        logger.info('click inventory show more')
        time.sleep(random.randint(4, 7))

        # click Manage FBA Inventory
        try:
            reports = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'FBA_MYI_UNSUPPRESSED_INVENTORY')))
            time.sleep(random.randint(4, 7))
            webdriver.ActionChains(self.driver).move_to_element(reports).perform()
            reports.click()
            logger.info('click Manage FBA Inventory')
            time.sleep(random.randint(5, 9))
        except Exception as e:
            print(e)

        # click Request .txt Download
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="requestCsvTsvDownload"]/tr[1]/td[3]/button'))).click()
        except Exception as e:
            print(e)
        logger.info('Request .txt Download')
        time.sleep(random.randint(20, 40))

        # click download
        try:
            download_button = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr/td[5]/a')))
            download_button.click()
        except Exception as e:
            print(e)
        logger.info('downloading')
        time.sleep(random.randint(1, 7))

        try:
            download_link = download_button.get_attribute("href")
            logger.info(download_link)
            FBA_inventory = re.findall(r"_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA__(\d*)\.txt", download_link)[0]
            logger.info(FBA_inventory)
            return FBA_inventory + '.txt'
        except Exception as e:
            print(e)

    def go_to_advertising_reports_download_page(self):

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

            # click advertising reports
            try:
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[6]'))).click()
                logger.info('click advertising reports')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # choose Advertised product
        try:
            # click drop down
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[2]/div[1]/div[2]/span/span'))).click()

            # click daily
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dropdown1_2"]'))).click()
        except Exception as e:
            print(e)
        logger.info('choose Advertised product')
        time.sleep(random.randint(4, 7))

        # choose daily
        try:
            # click drop down
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[2]/div[2]/div[2]/span/span'))).click()

            # click daily
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dropdown2_1"]'))).click()
        except Exception as e:
            print(e)
        logger.info('choose daily')
        time.sleep(random.randint(4, 7))

        # click create report
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[1]/span/span/input'))).click()
        except Exception as e:
            print(e)
        logger.info('click create report')
        time.sleep(random.randint(4, 7))

        # click download
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[3]/div/div/div/div[2]/div/div[5]/span/span/a'))).click()
        except Exception as e:
            print(e)
        logger.info('click download')
        time.sleep(random.randint(4, 7))

        dir_list = os.listdir(os.path.expanduser('~/Downloads/'))
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(os.path.expanduser('~/Downloads/'), x)))
        return dir_list[-1]
        # return 'Sponsored Products Search term report.xlsx'

    def go_to_advertising_search_term_reports_download_page(self):

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

            # click advertising reports
            try:
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[6]'))).click()
                logger.info('click advertising reports')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)

        # choose daily
        try:
            # click drop down
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[2]/div[2]/div[2]/span/span'))).click()

            # click daily
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dropdown1_1"]'))).click()
        except Exception as e:
            print(e)
        logger.info('choose daily')
        time.sleep(random.randint(4, 7))

        # click create report
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/section/div[1]/span/span/input'))).click()
        except Exception as e:
            print(e)
        logger.info('click create report')
        time.sleep(random.randint(4, 7))

        # click download
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="tresah"]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[3]/div/div/div/div[2]/div/div[5]/span/span/a'))).click()
        except Exception as e:
            print(e)
        logger.info('click download')
        time.sleep(random.randint(4, 7))

        dir_list = os.listdir(os.path.expanduser('~/Downloads/'))
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(os.path.expanduser('~/Downloads/'), x)))
        return dir_list[-1]

        # return 'Sponsored Products Search term report.xlsx'

    def go_to_campaigns_bulk_report_download(self):

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

            # click advertising reports
            try:
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[6]'))).click()
                logger.info('click advertising reports')
                time.sleep(random.randint(4, 7))
                break
            except Exception as e:
                print(e)


        # click bulk operations
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tresah"]/div/div/div[1]/nav/ul/a[3]'))).click()
        except Exception as e:
            print(e)
        logger.info('click bulk operations')
        time.sleep(random.randint(4, 7))

        # click create spreadsheet for download
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="request-entity-report-submit"]/span/input'))).click()
        except Exception as e:
            print(e)
        logger.info('click create spreadsheet for download')
        time.sleep(random.randint(4, 7))
        self.scroll_down()

        # click download
        while True:
            try:
                self.driver.refresh()
                time.sleep(random.randint(5, 15))
                try:
                    download_button = WebDriverWait(self.driver, 3, 0.5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="downloadHistoryId"]/tbody/tr[2]/td[2]/div/a')))
                    download_button.click()
                    logger.info('click download')
                    time.sleep(random.randint(4, 7))

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
                WebDriverWait(self.driver, 40, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-navtab-reports"]/ul/li[4]'))).click()
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
        logger.info('click detail page sales and traffic')
        time.sleep(random.randint(4, 7))

        # click download drop down
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="export"]/div'))).click()
        except Exception as e:
            print(e)
        logger.info('click download drop down')
        time.sleep(random.randint(4, 7))

        # choose csv
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadCSV"]'))).click()
        except Exception as e:
            print(e)
        logger.info('choose csv')
        time.sleep(random.randint(4, 7))
        return 'BusinessReport-' + datetime.date.today().strftime("%m-%d-%y") + '.csv'

    def upload_files(self, url, file_name, email, password, seller_id, file_type, country):

        rootdir = os.path.expanduser('~/Downloads/')
        logger.info(rootdir)
        file_path = rootdir + file_name
        logger.info(file_path)
        logger.info("gideon login")
        js = 'window.open("https://300gideon.com/login");'
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
            date_elem.value = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
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
            date_elem.value = datetime.date.today().strftime("%Y-%m-%d")

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

        try:
            time.sleep(random.randint(1, 5))
            self.driver.close()
            self.driver.switch_to_window(handles[0])
            os.remove(file_path)
        except Exception as e:
            print(e)

    def close_webdriver(self):
        self.driver.quit()

class MultiCronTrigger(BaseTrigger):

    triggers = []

    def __init__(self, triggers):
        self.triggers = triggers

    def get_next_fire_time(self, previous_fire_time, now):
        min_next_fire_time = None
        for trigger in self.triggers:
            # 从trigger对象中取出下一个要执行的时间点，与当前时间对比
            next_fire_time = trigger.get_next_fire_time(previous_fire_time, now)
            if next_fire_time is None:
                continue
            if min_next_fire_time is None:
                min_next_fire_time = next_fire_time
            if next_fire_time < min_next_fire_time:
                min_next_fire_time = next_fire_time
        return min_next_fire_time
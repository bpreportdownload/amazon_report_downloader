import time
import random
import re
import os
import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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



    def scroll_down(self,):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def go_to_listings_download_page(self):

        # 移动鼠标到inventory
        for i in range(0, 3):
            click = 'false'
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
                length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-inventory"]/ul/li'))
                logger.info(length)
                for i in range(1, length):
                    time.sleep(random.randint(3, 7))
                    report_name = self.driver.find_element_by_xpath(
                        '//*[@id="sc-navtab-inventory"]/ul/li[{}]'.format(i)).text.strip()
                    if report_name == 'Inventory Reports':
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
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'a-autoid-0-announce'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click Report Type drop down')
        time.sleep(random.randint(4, 7))

        # click all listing report
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.ID, 'dropdown1_7'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click all listing report')
        time.sleep(random.randint(4, 7))

        # click request report button
        try:
            WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="a-autoid-5"]/span/input'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
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
        logger.info('All+Listings+Report+' + datetime.datetime.utcnow().date().strftime("%m-%d-%Y") + ".txt")
        time.sleep(random.randint(20, 50))
        return 'All+Listings+Report+' + datetime.datetime.utcnow().date().strftime("%m-%d-%Y") + ".txt"

    def close_tooltips(self):
        # close tooltips
        try:
            self.driver.find_element_by_xpath('//*[@id="step-0"]/div[2]/button').click()
        except:
            pass

    def go_to_today_orders_download_page(self):

        # 移动鼠标到reports
        for i in range(0, 3):
            click = 'false'
            try:
                reports = WebDriverWait(self.driver, 20, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(7, 9))
            except Exception as e:
                print(e)

            # click fulfillments
            try:
                length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                logger.info(length)
                for i in range(1, length):
                    time.sleep(random.randint(3, 7))
                    logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                    report_name = self.driver.find_element_by_xpath(
                        '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                    logger.info(report_name)
                    if report_name == 'Fulfillment':
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
                EC.presence_of_element_located((By.ID, 'FlatFileAllOrdersReport'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click all orders')
        time.sleep(random.randint(1, 7))

        # click order date drop down
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'eventDateType'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        time.sleep(random.randint(1, 7))

        # select Last Updated Date
        try:
            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="eventDateType"]/select/option[2]'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('choose Last Updated Date')
        time.sleep(random.randint(1, 7))

        # click last date drop down
        try:
            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.ID, 'downloadDateDropdown'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        time.sleep(random.randint(1, 7))

        # select Exact Date
        try:
            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadDateDropdown"]/option[6]'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        time.sleep(random.randint(1, 7))

        # From today to today
        try:
            from_elem = WebDriverWait(self.driver, 40, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#fromDateDownload')))
            today = datetime.date.today().strftime("%m/%d/%Y")
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
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('select today')
        time.sleep(random.randint(4, 7))

        # click download
        try:
            WebDriverWait(self.driver, 120, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="requestDownload"]/td[2]/button'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('download request')
        time.sleep(random.randint(1, 7))

        try:
            WebDriverWait(self.driver, 900, 0.5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a/span/span'))).click()
            logger.info('downloading')
            time.sleep(random.randint(20, 50))
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
        except Exception as e:
            print(e)
            self.driver.quit()


    def go_to_orders_download_page(self):

        # 移动鼠标到reports
        for i in range(0, 3):
            click = 'false'
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
                length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                logger.info(length)
                for i in range(1, length):
                    time.sleep(random.randint(3, 7))
                    logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                    report_name = self.driver.find_element_by_xpath('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                    if report_name == 'Fulfillment':
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
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'FlatFileAllOrdersReport'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click all orders')
        time.sleep(random.randint(1, 7))

        # click order date drop down
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'eventDateType'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        time.sleep(random.randint(1, 7))

        # select Last Updated Date
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="eventDateType"]/select/option[2]'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('choose Last Updated Date')
        time.sleep(random.randint(1, 7))

        # click last date drop down
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'downloadDateDropdown'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        time.sleep(random.randint(1, 7))

        # select Last Updated Date
        try:
            pt = '//*[@id="downloadDateDropdown"]/option[{}]'.format(random.randint(2, 3))
            logger.info(pt)
            WebDriverWait(self.driver, 20, 0.5).until(
                EC.presence_of_element_located((By.XPATH, pt))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('choose 3/7 Date')
        time.sleep(random.randint(1, 7))

        # click download
        try:
            WebDriverWait(self.driver, 120, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requestDownload"]/td[2]/button'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('download request')
        time.sleep(random.randint(1, 7))


        try:
            WebDriverWait(self.driver, 900, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[4]/a/span/span'))).click()
            logger.info('downloading')
            time.sleep(random.randint(20, 50))
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
        except Exception as e:
            print(e)
            self.driver.quit()

    def go_to_FBA_shipment_download_page(self):
        # 移动鼠标到reports
        for i in range(0, 3):
            click = 'false'
            try:
                reports = WebDriverWait(self.driver, 940, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(7, 9))
            except Exception as e:
                print(e)

            # click fulfillments
            try:
                length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                logger.info(length)
                for i in range(1, length):
                    time.sleep(random.randint(3, 7))
                    logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                    report_name = self.driver.find_element_by_xpath(
                        '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                    if report_name == 'Fulfillment':
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
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.ID, 'AFNShipmentReport'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click Amazon Fulfilled Shipments')
        time.sleep(random.randint(1, 7))

        # click event date drop down
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.ID, 'downloadDateDropdown'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click event date drop down')
        time.sleep(random.randint(1, 7))

        # choose date range
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#downloadDateDropdown > option:nth-child({})'.format(random.randint(3, 5))))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('date range')
        time.sleep(random.randint(1, 7))

        # click  Request .txt Download
        try:
            WebDriverWait(self.driver, 960, 0.5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="requestCsvTsvDownload"]/tr[1]/td[3]/button'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click  Request .txt Download')
        time.sleep(random.randint(1, 7))
        # click download
        try:
            download_button = WebDriverWait(self.driver, 900, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr[1]/td[5]/a')))
            download_button.click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('downloading')
        time.sleep(random.randint(20, 50))

        try:
            download_link = download_button.get_attribute("href")
            logger.info(download_link)
            FBA_shippment_name = re.findall(r"GET_AMAZON_FULFILLED_SHIPMENTS_DATA__(\d*)\.txt", download_link)[0]
            logger.info(FBA_shippment_name)
            return FBA_shippment_name + '.txt'
        except Exception as e:
            print(e)
            self.driver.quit()


    def go_to_finance_download_page(self):

        # 移动鼠标到reports
        for i in range(0, 8):
            click = 'false'
            try:
                reports = WebDriverWait(self.driver, 940, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(5, 9))

                # click payments
                try:
                    length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                    logger.info(length)
                    for i in range(1, length):
                        time.sleep(random.randint(3, 7))
                        logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                        report_name = self.driver.find_element_by_xpath(
                            '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                        if report_name == 'Payments':
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
            except Exception as e:
                print(e)


        # click data range report
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#PaymentTabs > div > ul > li:nth-child(4)'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click data range report')
        time.sleep(random.randint(4, 7))

        # click generate report
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrGenerateReportButton'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click data range report')
        time.sleep(random.randint(4, 7))

        # select date
        try:
            start = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrFromDate')))
            start.click()
            seven_days_ago = (datetime.date.today() - datetime.timedelta(days=random.randint(7, 10))).strftime("%m/%d/%Y")
            start.send_keys(seven_days_ago)
            time.sleep(random.randint(3, 7))
            end = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrToDate')))
            end.click()
            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")
            end.send_keys(yesterday)
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('select date')
        time.sleep(random.randint(4, 7))

        # generate
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#drrGenerateReportsGenerateButton'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('select date')
        time.sleep(random.randint(10, 20))
        self.scroll_down()
        self.driver.refresh()
        time.sleep(random.randint(20, 30))
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
            self.driver.quit()

    def go_to_FBA_inventory_download_page(self):

        # 移动鼠标到reports
        for i in range(0, 3):
            click = 'false'
            try:
                reports = WebDriverWait(self.driver, 940, 0.5).until(
                    EC.presence_of_element_located((By.ID, 'sc-navtab-reports')))
                time.sleep(random.randint(4, 7))
                webdriver.ActionChains(self.driver).move_to_element(reports).perform()
                logger.info('go to reports')
                time.sleep(random.randint(5, 9))
            except Exception as e:
                print(e)

            # click fulfillments
            try:
                length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                logger.info(length)
                for i in range(1, length):
                    time.sleep(random.randint(3, 7))
                    logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                    report_name = self.driver.find_element_by_xpath(
                        '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                    if report_name == 'Fulfillment':
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
                EC.presence_of_element_located((By.XPATH, '//*[@id="sc-sidepanel"]/div/ul[2]/li[23]/a'))).click()
        except Exception as e:
            print(e)
            try:
                WebDriverWait(self.driver, 910, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="sc-sidepanel"]/div/ul[2]/li[21]/a'))).click()
            except Exception as e:
                print(e)
        logger.info('click inventory show more')
        time.sleep(random.randint(4, 7))

        # click Manage FBA Inventory
        try:
            reports = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.ID, 'FBA_MYI_UNSUPPRESSED_INVENTORY')))
            time.sleep(random.randint(4, 7))
            webdriver.ActionChains(self.driver).move_to_element(reports).perform()
            reports.click()
            logger.info('click Manage FBA Inventory')
            time.sleep(random.randint(5, 9))
        except Exception as e:
            print(e)
            self.driver.quit()

        # click Request .txt Download
        try:
            WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="requestCsvTsvDownload"]/tr[1]/td[3]/button'))).click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('Request .txt Download')
        time.sleep(random.randint(20, 40))

        # click download
        try:
            download_button = WebDriverWait(self.driver, 940, 0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="downloadArchive"]/table/tbody/tr/td[5]/a')))
            download_button.click()
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('downloading')
        time.sleep(random.randint(20, 50))

        try:
            download_link = download_button.get_attribute("href")
            logger.info(download_link)
            FBA_inventory = re.findall(r"_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA__(\d*)\.txt", download_link)[0]
            logger.info(FBA_inventory)
            return FBA_inventory + '.txt'
        except Exception as e:
            print(e)
            self.driver.quit()

    def go_to_advertising_reports_download_page(self):

        # 移动鼠标到reports
        for i in range(0, 3):
            click = 'false'
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
                length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                logger.info(length)
                for i in range(1, length):
                    time.sleep(random.randint(3, 7))
                    logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                    report_name = self.driver.find_element_by_xpath(
                        '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                    if report_name == 'Advertising Reports':
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
        try:
            # click drop down
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
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('choose Advertised product')
        time.sleep(random.randint(4, 7))

        # select date
        try:
            # click drop down

            report_period = "document.querySelector('#cards-container > div.sc-chPdSV.hJxqxz > div > div.sc-1xc1ftl-1.evvFrQ > table > tbody > tr:nth-child(4) > td > button').click()"
            self.driver.execute_script(report_period)
            time.sleep(random.randint(4, 7))

            js = "document.querySelector('#portal > div > div > div > div.sc-11mc28f-3.jWiMFK > button:nth-child(%s)').click();" % random.randint(1, 5)
            logger.info(js)
            self.driver.execute_script(js)
            logger.info('click drop down')

            time.sleep(random.randint(4, 7))
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('select date')
        time.sleep(random.randint(4, 7))

        # click create report
        try:
            create_report = "document.querySelector('#run-report-button').click()"
            self.driver.execute_script(create_report)
        except Exception as e:
            print(e)
            self.driver.quit()
        logger.info('click create report')
        time.sleep(random.randint(100, 200))

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
                time.sleep(random.randint(5, 9))
            except Exception as e:
                print(e)

            # click advertising reports
            try:
                length = len(self.driver.find_elements_by_xpath('//*[@id="sc-navtab-reports"]/ul/li'))
                logger.info(length)
                for i in range(1, length):
                    time.sleep(random.randint(3, 7))
                    logger.info(('//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)))
                    report_name = self.driver.find_element_by_xpath(
                        '//*[@id="sc-navtab-reports"]/ul/li[{}]'.format(i)).text.strip()
                    if report_name == 'Advertising Reports':
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
        try:
            js_click_download = "document.querySelector('#advertising-reports > div > div > div > div.ReactTable > div.rt-table > div.rt-tbody > div:nth-child(1) > div > div:nth-child(2) > span > a').click();"
            self.driver.execute_script(js_click_download)
            logger.info('click download')
            time.sleep(random.randint(4, 7))
        except Exception as e:
            print(e)

        dir_list = os.listdir(os.path.expanduser('~/Downloads/'))
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(os.path.expanduser('~/Downloads/'), x)))
        return dir_list[-1]
        # return 'Sponsored Products Search term report.xlsx'

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

    def upload_files(self, url, file_name, email, password, seller_id, file_type, country):

        rootdir = os.path.expanduser('~/Downloads/')
        logger.info(rootdir)
        file_path = rootdir + file_name
        logger.info(file_path)
        logger.info("gideon login")

        try:
            js = 'window.open("https://300gideon.com/login");'
            self.driver.execute_script(js)

            handles = self.driver.window_handles
            self.driver.switch_to_window(handles[1])
        except Exception as e:
            print(e)

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
            date_elem.value = (datetime.datetime.utcnow().date() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
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
            date_elem.value = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")

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
            time.sleep(random.randint(20, 30))
            self.driver.close()
            self.driver.switch_to_window(handles[0])
            os.remove(file_path)
        except Exception as e:
            print(e)
            self.driver.quit()

    def close_webdriver(self):
        self.driver.quit()

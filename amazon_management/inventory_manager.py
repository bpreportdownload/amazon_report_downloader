import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException)
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert

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
            'continue_selector': '#interstitialPageContinue-announce'
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

        time.sleep(3)
        Alert(self.driver).accept()
        # try:
        #     confirm_window = WebDriverWait(self.driver, 10).until(
        #         EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "remove the product or products")))
        #     Alert(self.driver).accept()
        # except (NoSuchElementException, TimeoutException):
        #     raise RuntimeError('Could not select delete option - %s' % self.selectors['bulk_action_select_selector'])

        time.sleep(3)

        if '/inventory/confirmAction' in self.driver.current_url:
            while True:
                try:
                    continue_elem = WebDriverWait(self.driver, 12).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['continue_selector'])))
                    script = 'document.querySelector("{}").click()'.format(
                        self.selectors['continue_selector'])
                    self.driver.execute_script(script)
                    # continue_elem.click()
                    break
                except StaleElementReferenceException:
                    pass
                except WebDriverException as e:
                    if e.msg.find('is not clickable') != -1:
                        logger.exception(e)
                        continue

                    raise e
                except  (NoSuchElementException, TimeoutException):
                    raise RuntimeError(
                        'Could not find continue element - %s' % self.selectors['continue_selector'])

            try:
                WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Thanks for suggesting changes to the catalog')]")))
                logger.info('Selected products are deleted!')
            except (NoSuchElementException, TimeoutException):
                logger.warning('Delete result could not determined!')
                result = False

        return result

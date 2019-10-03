import os
import sys
import random
import time

import click
import yaml

from amazon_management import logger, get_shared_driver, MARKETPLACE_MAPPING
from amazon_management.utils import YamlConfigLoader
from amazon_management.helpers import SellerLoginHelper
from amazon_management.inventory_manager import InventoryManager


@click.command()
@click.option('-c', '--config_path', help='Configuration file path.')
@click.option('-k', '--keywords_path', help='Keywords file path.')
def clear_inv_by_sku(config_path, keywords_path):
    config_path = os.path.abspath(os.path.expanduser(config_path))
    if not os.path.isfile(config_path):
        logger.error('Could not find configuration file - %s', config_path)
        sys.exit(0)

    cl = YamlConfigLoader(config_path)
    config = cl.load()

    keywords_path = os.path.abspath(os.path.expanduser(keywords_path))
    if not os.path.isfile(keywords_path):
        logger.error('Could not find keywords file - %s', keywords_path)
        sys.exit(0)

    keywords = []
    with open(keywords_path) as fh:
        for line in fh:
            keyword = line.strip()
            if keyword:
                keywords.append(keyword)

    logger.info('Keywords to clear: %s', ','.join(keywords))

    marketplace = config['account']['marketplace'].lower()
    email = config['account']['email']
    password = config['account']['password']

    driver = get_shared_driver(marketplace)
    helper = SellerLoginHelper(driver, email, password, marketplace)
    inv_manager = InventoryManager(driver)

    inventory_url_template = 'https://{}/inventory?tbla_myitable=sort:%7B"sortOrder"%3A"DESCENDING"%2C"sortedColumnId"%3A"date"%7D;search:'
    inventory_url = inventory_url_template.format(MARKETPLACE_MAPPING.get(marketplace)['sellercentral'])
    driver.get(inventory_url)
    while helper.is_login_required():
            logger.info('Login required! Trying to login...')

            helper.login()

            wait_time = 180
            while wait_time > 0:
                wait_time -= 1
                logger.debug('Waiting for login...')
                if helper.is_login_required():
                    time.sleep(1)
                else:
                    break

            if wait_time <= 0:
                logger.error('Could not login to seller central, exit!')
                sys.exit(1)

            driver.get(inventory_url)

    helper.pick_marketplace()
    logger.info('Picked marketplace!')

    try:
        while len(keywords) > 0:
            keyword = random.choice(keywords)
            search_keyword_url = inventory_url + keyword
            driver.get(search_keyword_url)

            total_products_cnt = inv_manager.get_total_products_cnt()
            total_product_pages_cnt = inv_manager.get_total_product_pages_cnt()
            logger.info(
                'keyword: %s, total_products_cnt: %d, total_product_pages_cnt: %d',
                keyword, total_products_cnt, total_product_pages_cnt)

            if total_products_cnt <= 0:
                logger.info('Could not find product match keyword %s', keyword)
                keywords.remove(keyword)
                continue

            if total_product_pages_cnt > 1:
                page = random.randrange(1, total_product_pages_cnt)
                inv_manager.go_to_page(page)
                logger.info('Go to page %d', page)

            inv_manager.scroll_down()
            logger.info('Wait 3 seconds until products loading complete!')
            time.sleep(3)
            inv_manager.scroll_down()
            inv_manager.select_all()
            inv_manager.delete_selected()

            time.sleep(3)
    finally:
        driver.quit()

if __name__ == '__main__':
    clear_inv_by_sku()

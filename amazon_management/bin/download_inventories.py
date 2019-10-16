
import os
import sys
import time
import click


from amazon_management import logger, get_shared_driver, MARKETPLACE_MAPPING
from amazon_management.utils import YamlConfigLoader
from amazon_management.helpers import SellerLoginHelper
from amazon_management.inventory_manager import Download
from apscheduler.schedulers.blocking import BlockingScheduler

# @click.command()
def download_inventories():
    config_path = './inventory_download.yml'
    config_path = os.path.abspath(os.path.expanduser(config_path))
    if not os.path.isfile(config_path):
        logger.error('Could not find configuration file - %s', config_path)
        sys.exit(0)

    cl = YamlConfigLoader(config_path)
    config = cl.load()

    marketplace = config['account']['marketplace'].lower()
    email = config['account']['email']
    password = config['account']['password']
    gideon_email = config['account']['gideon_email']
    gideon_password = config['account']['gideon_password']
    seller_id = config['account']['seller_id']




    driver = get_shared_driver(marketplace)
    helper = SellerLoginHelper(driver, email, password, marketplace)
    downloader = Download(driver)

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

        time.sleep(7)

        driver.get(inventory_url)

    helper.pick_marketplace()
    logger.info('Picked marketplace!')

    try:
        downloader.close_tooltips()
        file_name = downloader.go_to_orders_download_page()
        logger.info(file_name)
        downloader.upload_files("https://300gideon.com/import_orders", file_name, gideon_email, gideon_password, seller_id)
        FBA_shippment_name = downloader.go_to_FBA_shipment_download_page()
        downloader.upload_FBA_shippment_files("https://300gideon.com/import_orders", FBA_shippment_name, gideon_email, gideon_password, seller_id)

        listing_report = downloader.go_to_listings_download_page()
        downloader.upload_listings_files("https://300gideon.com/import_listings", listing_report, gideon_email, gideon_password, seller_id)

        FBA_inventory = downloader.go_to_FBA_inventory_download_page()
        downloader.upload_FBA_inventory_files("https://300gideon.com/import_inventory", FBA_inventory, gideon_email,
                                         gideon_password, seller_id)

        FBA_inventory = downloader.go_to_FBA_inventory_download_page()
        downloader.upload_FBA_inventory_files("https://300gideon.com/import_inventory", FBA_inventory, gideon_email,
                                              gideon_password, seller_id)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    download_inventories()


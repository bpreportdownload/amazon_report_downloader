
import os
import sys
import time
import click
import random

from amazon_management import logger, get_shared_driver, MARKETPLACE_MAPPING
from amazon_management.utils import YamlConfigLoader
from amazon_management.helpers import SellerLoginHelper
from amazon_management.inventory_manager import Download
from amazon_management.inventory_manager import MultiCronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


@click.command()
@click.option('-c', '--report', help='[1.order_report 2.FBA_shipment_report 3.finance_report 4.advertising_report 5.campaigns_bulk_report 6.advertising_search_term_report 7.listings_report 8.FBA_inventory_report 9.business_report]')
def download_report(report):
    logger.info(report)
    config_path = './amazon_management/inventory_download.yml'
    config_path = os.path.abspath(os.path.expanduser(config_path))
    # if not os.path.isfile(config_path):
    #     logger.error('Could not find configuration file - %s', config_path)
    #     sys.exit(0)
    #
    cl = YamlConfigLoader(config_path)
    config = cl.load()

    for marketplace in config['account']['marketplace']:
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
            marketplace = marketplace.upper()
            logger.info(marketplace)
            downloader.close_tooltips()

            if report == "order_report":
                try:
                    file_name = downloader.go_to_orders_download_page()
                    downloader.upload_files("https://300gideon.com/import_orders", file_name, gideon_email, gideon_password, seller_id, "orders_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "FBA_shipment_report":
                try:
                    file_name = downloader.go_to_FBA_shipment_download_page()
                    downloader.upload_files("https://300gideon.com/import_orders", file_name, gideon_email, gideon_password, seller_id, "order_shipments_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "finance_report":
                try:
                    file_name = downloader.go_to_finance_download_page()
                    downloader.upload_files("https://300gideon.com/import_finances", file_name, gideon_email, gideon_password, seller_id, "finances_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "advertising_report":
                try:
                    file_name = downloader.go_to_advertising_reports_download_page()
                    downloader.upload_files("https://300gideon.com/import_ads", file_name, gideon_email,
                                                     gideon_password, seller_id, "ads_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "campaigns_bulk_report":
                try:
                    file_name = downloader.go_to_campaigns_bulk_report_download()
                    downloader.upload_files("https://300gideon.com/import_campaigns", file_name, gideon_email,
                                                          gideon_password, seller_id, "campaigns_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "advertising_search_term_report":
                try:
                    file_name = downloader.go_to_advertising_search_term_reports_download_page()
                    downloader.upload_files("https://300gideon.com/import_campaigns", file_name, gideon_email,
                                                          gideon_password, seller_id, "searchterms_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "listings_report":
                try:
                    file_name = downloader.go_to_listings_download_page()
                    downloader.upload_files("https://300gideon.com/import_listings", file_name, gideon_email,
                                                          gideon_password, seller_id, "listings_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "FBA_inventory_report":
                try:
                    file_name = downloader.go_to_FBA_inventory_download_page()
                    downloader.upload_files("https://300gideon.com/import_inventory", file_name, gideon_email,
                                                          gideon_password, seller_id, "inventory_file", marketplace)
                except Exception as e:
                    print(e)

            if report == "business_report":
                try:
                    file_name = downloader.go_to_business_report_download()
                    downloader.upload_files("https://300gideon.com/import_business", file_name, gideon_email,
                                                          gideon_password, seller_id, "business_file", marketplace)

                except Exception as e:
                    print(e)

            downloader.close_webdriver()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    download_report()





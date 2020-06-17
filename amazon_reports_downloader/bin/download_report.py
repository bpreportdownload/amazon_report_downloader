
import os
import sys
import time
import click
import random

from amazon_reports_downloader import logger, get_shared_driver, MARKETPLACE_MAPPING
from amazon_reports_downloader.utils import YamlConfigLoader
from amazon_reports_downloader.helpers import SellerLoginHelper
from amazon_reports_downloader.inventory_manager import Download

@click.command()
@click.option('-c', '--report', help='[1.order_report 2.FBA_shipment_report 3.finance_report 4.advertising_report 5.campaigns_bulk_report 6.advertising_search_term_report 7.listings_report 8.FBA_inventory_report 9.business_report]')

def download_report(report):
    logger.info(report)
    config_path = './amazon_reports_downloader/inventory_download.yml'
    config_path = os.path.abspath(os.path.expanduser(config_path))
    if not os.path.isfile(config_path):
        logger.error('Could not find configuration file - %s', config_path)
        sys.exit(0)

    cl = YamlConfigLoader(config_path)
    config = cl.load()

    if report == "add_inventory":
        inventory_path = './amazon_reports_downloader/inventory.yml'
        inventory_path = os.path.abspath(os.path.expanduser(inventory_path))
        if not os.path.isfile(inventory_path):
            logger.error('Could not find configuration file - %s', inventory_path)
            sys.exit(0)
        inventory = YamlConfigLoader(inventory_path)
        inventory_config = inventory.load()

        email = config['account']['email']
        password = config['account']['password']
        seller_id = config['account']['seller_id']
        logger.info("parse config")
        for marketplace in inventory_config['account']['marketplaces']:
            logger.info(marketplace)
            try:
                if marketplace == 'us':
                    units = inventory_config['account']['us_market']['units']
                    package_l = inventory_config['account']['us_market']['package_l']
                    package_w = inventory_config['account']['us_market']['package_w']
                    package_h = inventory_config['account']['us_market']['package_h']
                    package_wight = inventory_config['account']['us_market']['package_wight']
                    shipment_name = inventory_config['account']['us_market']['shipment_name']
                    shipment_number = inventory_config['account']['us_market']['shipment_number']
                    shipment_id = inventory_config['account']['us_market']['shipment_id']
                    start = inventory_config['account']['us_market']['start']
                    domain = 'com'
                    for sku in inventory_config['account']['us_market']['skus']:
                        logger.info(sku)
                        time.sleep(random.randint(1, 7))
                        driver = get_shared_driver(marketplace)
                        downloader = Download(driver)
                        helper = SellerLoginHelper(driver, email, password, marketplace)
                        seller_central_url = 'https://sellercentral.amazon.com/home'

                        driver.get(seller_central_url)
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

                            driver.get(seller_central_url)
                        logger.info('begin to pick marketplace')
                        helper.pick_marketplace()
                        logger.info('Picked marketplace!')

                        try:
                            marketplace = marketplace.upper()
                            logger.info(marketplace)
                            downloader.close_tooltips()

                            downloader.add_inventory(domain, seller_id, sku, units, package_l, package_w, package_h, package_wight,
                                                     shipment_name, shipment_number, shipment_id, start)
                            downloader.close_webdriver()
                        except Exception as e:
                            print(e)
                if marketplace == 'ca':
                    units = inventory_config['account']['ca_market']['units']
                    package_l = inventory_config['account']['ca_market']['package_l']
                    package_w = inventory_config['account']['ca_market']['package_w']
                    package_h = inventory_config['account']['ca_market']['package_h']
                    package_wight = inventory_config['account']['ca_market']['package_wight']
                    shipment_name = inventory_config['account']['ca_market']['shipment_name']
                    domain = 'ca'
                    shipment_number = inventory_config['account']['ca_market']['shipment_number']
                    shipment_id = inventory_config['account']['ca_market']['shipment_id']
                    start = inventory_config['account']['ca_market']['start']
                    domain = 'com'
                    for sku in inventory_config['account']['ca_market']['skus']:
                        logger.info(sku)
                        time.sleep(random.randint(1, 7))
                        driver = get_shared_driver(marketplace)
                        downloader = Download(driver)
                        helper = SellerLoginHelper(driver, email, password, marketplace)
                        seller_central_url = 'https://sellercentral.amazon.com/home'

                        driver.get(seller_central_url)
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

                            driver.get(seller_central_url)
                        logger.info('begin to pick marketplace')
                        helper.pick_marketplace()
                        logger.info('Picked marketplace!')

                        try:
                            marketplace = marketplace.upper()
                            logger.info(marketplace)
                            downloader.close_tooltips()

                            downloader.add_inventory(domain, seller_id, sku, units, package_l, package_w, package_h,
                                                     package_wight,
                                                     shipment_name, shipment_number, shipment_id, start)
                            downloader.close_webdriver()
                        except Exception as e:
                            print(e)

            except Exception as e:
                print(e)


    for marketplace in config['account']['marketplace']:
        logger.info(marketplace)
        email = config['account']['email']
        password = config['account']['password']
        gideon_email = config['account']['gideon_email']
        gideon_password = config['account']['gideon_password']
        seller_id = config['account']['seller_id']
        seller_profit_domain = config['account']['domain']

        domain = 'com'
        if marketplace == 'ca':
            domain = 'ca'
        if report == 'review_info':

            for seller_id in config['account']['seller_ids']:

                logger.info(seller_id)

                try:
                    driver = get_shared_driver(marketplace)
                    downloader = Download(driver)
                    downloader.review_info_scrapy(domain, seller_id, seller_profit_domain)
                except Exception as e:
                    downloader.save_page(e)
            downloader.close_webdriver()
            continue

        if report == 'listing_info':
            driver = get_shared_driver(marketplace)
            downloader = Download(driver)
            logger.info(seller_id)
            try:
                downloader.listing_info_scrapy(domain, seller_id, seller_profit_domain)
                downloader.close_webdriver()
            except Exception as e:
                downloader.save_page(e)
            continue

        driver = get_shared_driver(marketplace)
        time.sleep(15)
        helper = SellerLoginHelper(driver, email, password, marketplace)
        downloader = Download(driver)

        seller_central_url = 'https://sellercentral.amazon.com/home'

        # inventory_url_template = 'https://{}/inventory?tbla_myitable=sort:%7B"sortOrder"%3A"DESCENDING"%2C"sortedColumnId"%3A"date"%7D;search:'
        # inventory_url = inventory_url_template.format(MARKETPLACE_MAPPING.get(marketplace)['sellercentral'])
        driver.get(seller_central_url)
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

            driver.get(seller_central_url)
        logger.info('begin to pick marketplace')
        helper.pick_marketplace()
        logger.info('Picked marketplace!')

        try:
            marketplace = marketplace.upper()
            logger.info(marketplace)
            downloader.close_tooltips()

            if report == "order_report_today":
                index = random.randint(0, 7)
                logger.info(index)

                for i in range(7):
                    logger.info(i)
                    if (i + index) % 7 == 0:
                        try:
                            file_name = downloader.go_to_today_orders_download_page()
                            downloader.upload_files(seller_profit_domain + "/import_orders", file_name, gideon_email,
                                                    gideon_password, seller_id, "orders_file", marketplace, seller_profit_domain)
                        except Exception as e:
                            print(e)
                    else:
                        if (int(time.strftime("%H", time.localtime())) > 18) or (int(time.strftime("%H", time.localtime())) < 8):
                            if (i + index) % 7 == 1:
                                try:
                                    file_name = downloader.go_to_orders_download_page()
                                    downloader.upload_files(seller_profit_domain + "/import_orders", file_name, gideon_email,
                                                            gideon_password, seller_id, "orders_file", marketplace, seller_profit_domain)
                                except Exception as e:
                                    print(e)

                            if (i + index) % 7 == 2:
                                try:
                                    file_name = downloader.go_to_FBA_shipment_download_page()
                                    downloader.upload_files(seller_profit_domain + "/import_orders", file_name, gideon_email,
                                                            gideon_password, seller_id, "order_shipments_file", marketplace, seller_profit_domain)
                                except Exception as e:
                                    print(e)

                            if (i + index) % 7 == 3:
                                try:
                                    file_name = downloader.go_to_finance_download_page()
                                    downloader.upload_files(seller_profit_domain + "/import_finances", file_name, gideon_email,
                                                            gideon_password, seller_id, "finances_file", marketplace, seller_profit_domain)
                                except Exception as e:
                                    print(e)

                            if (i + index) % 7 == 4:
                                try:
                                    file_name = downloader.go_to_advertising_reports_download_page()
                                    downloader.upload_files(seller_profit_domain + "/import_ads", file_name, gideon_email,
                                                            gideon_password, seller_id, "ads_file", marketplace, seller_profit_domain)
                                except Exception as e:
                                    print(e)

                            if (i + index) % 7 == 5:
                                try:
                                    file_name = downloader.go_to_listings_download_page()
                                    downloader.upload_files(seller_profit_domain + "/import_listings", file_name, gideon_email,
                                                            gideon_password, seller_id, "listings_file", marketplace, seller_profit_domain)
                                except Exception as e:
                                    print(e)

                            if (i + index) % 7 == 6:
                                try:
                                    file_name = downloader.go_to_FBA_inventory_download_page()
                                    downloader.upload_files(seller_profit_domain + "/import_inventory", file_name, gideon_email,
                                                            gideon_password, seller_id, "inventory_file", marketplace, seller_profit_domain)
                                except Exception as e:
                                    print(e)
            if report == "advertising_report":
                try:
                    file_name = downloader.go_to_advertising_reports_download_page()
                    downloader.upload_files(seller_profit_domain + "/import_ads", file_name, gideon_email,
                                            gideon_password, seller_id, "ads_file", marketplace, seller_profit_domain)
                except Exception as e:
                    print(e)

            if report == "FBA_inventory_report":
                try:
                    file_name = downloader.go_to_FBA_inventory_download_page()
                    downloader.upload_files(seller_profit_domain + "/import_inventory", file_name, gideon_email,
                                            gideon_password, seller_id, "inventory_file", marketplace, seller_profit_domain)
                except Exception as e:
                    print(e)

            if report == "finance_report":
                try:
                    file_name = downloader.go_to_finance_download_page()
                    downloader.upload_files(seller_profit_domain + "/import_finances", file_name, gideon_email,
                                            gideon_password, seller_id, "finances_file", marketplace, seller_profit_domain)
                except Exception as e:
                    print(e)

            if report == "listings_report":
                try:
                    file_name = downloader.go_to_listings_download_page()
                    downloader.upload_files(seller_profit_domain + "/import_listings", file_name, gideon_email,
                                            gideon_password, seller_id, "listings_file", marketplace, seller_profit_domain)
                except Exception as e:
                    print(e)

            if report == "order_report":
                try:
                    file_name = downloader.go_to_orders_download_page()
                    downloader.upload_files(seller_profit_domain + "/import_orders", file_name, gideon_email,
                                            gideon_password, seller_id, "orders_file", marketplace, seller_profit_domain)
                except Exception as e:
                    print(e)

            if report == "FBA_shipment_report":
                try:
                    file_name = downloader.go_to_FBA_shipment_download_page()
                    downloader.upload_files(seller_profit_domain + "/import_orders", file_name, gideon_email,
                                            gideon_password, seller_id, "order_shipments_file", marketplace, seller_profit_domain)
                except Exception as e:
                    print(e)


            downloader.close_webdriver()
        except Exception as e:
            logger.info("error occour")
            downloader.save_page()
            print(e)


if __name__ == '__main__':
    download_report()





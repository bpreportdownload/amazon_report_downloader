# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import sys
import time
import datetime
import logging
import logging.handlers

import click

import amazon_management
from amazon_management import (
    logger,
    get_shared_driver,
    shared_work_directory,
    SHIPPING_TEMPLATE_MAPPING
)
from amazon_management.helpers import SellerLoginHelper
from amazon_management.shipping_fee_calculator import ShippingFeeCalculator
from amazon_management.shipping_adjust_recorder import ShippingAdjustRecorder
from amazon_management.utils import YamlConfigLoader


@click.command()
@click.option('-c', '--config_path', help='Configuration file path.')
def update_shipping_price(config_path):
    log_file = os.path.join(shared_work_directory, 'shipping', 'update_shipping_price.log')
    level = logging.INFO
    max_bytes = 20 * 1024 ** 2
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=3)
    fh.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]:%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    if not config_path:
        logger.error('config_path is required to run.')
        sys.exit(1)

    config_path = os.path.abspath(os.path.expanduser(config_path))
    if not os.path.isfile(config_path):
        logger.error('Could not find configuration file - %s', config_path)
        sys.exit(1)

    cl = YamlConfigLoader(config_path)
    config = cl.load()

    marketplace = config['account']['marketplace'].lower()
    email = config['account']['email']
    password = config['account']['password']
    template_name = config['rules']['template_name']

    shipping_templates_url = SHIPPING_TEMPLATE_MAPPING.get(marketplace, None)
    if shipping_templates_url is None:
        logger.error('Marketplace %s is not supported!', marketplace)
        sys.exit(1)

    shipping_fee_calculator = ShippingFeeCalculator(config['rules'])
    price_adjust = shipping_fee_calculator.get_price_adjustment()
    if price_adjust == 0:
        logger.info('Shipping fee adjustment is 0, exit!')
        sys.exit(0)

    driver = get_shared_driver(marketplace)
    driver.get(shipping_templates_url)

    seller_login_helper = SellerLoginHelper(driver, email, password)
    if seller_login_helper.is_login_required():
        seller_login_helper.login()
        wait_time = 180
        while wait_time > 0:
            wait_time -= 1
            logger.debug('Waiting for login...')
            if seller_login_helper.is_login_required():
                time.sleep(1)
            else:
                break

        if wait_time <= 0:
            logger.error('Could not login to seller central, exit!')
            sys.exit(1)

        time.sleep(7)

        driver.get(shipping_templates_url)

    ShippingTemplateManager = getattr(
        amazon_management.shipping_template_managers,
        '{}ShippingTemplateManager'.format(marketplace.capitalize()))
    stm = ShippingTemplateManager(driver)
    if not stm.pick_marketplace():
        logger.error('Could not pick marketplace %s', marketplace)
        sys.exit(1)

    try:
        driver.get(shipping_templates_url)
        cur_shipping_fees = stm.get_shipping_fee()
        if cur_shipping_fees is None:
            logger.error('Could not identify current shipping fees')
            sys.exit(1)

        shipping_adjust_recorder = ShippingAdjustRecorder(marketplace)
        last_adjust_time, shipping_fees = shipping_adjust_recorder.get_last_adjust_record()
        shipping_adjusted = shipping_adjust_recorder.is_shipping_adjusted(last_adjust_time)
        if shipping_adjusted and shipping_fees == cur_shipping_fees:
            logger.info(
                'Shipping has already been adjusted, current time is %s, adjust time is %s!',
                datetime.datetime.now(), str(last_adjust_time))
            sys.exit(0)

        template_elem = stm.find_template_by_name(template_name)
        if template_elem is None:
            logger.error('Could not find template %s', template_name)
            sys.exit(1)

        template_choosen = stm.choose_template(template_elem)
        if not template_choosen:
            logger.error('Could not choose template %s', template_name)
            sys.exit(1)

        stm.trigger_edit_template()
        stm.change_shipping_price(price_adjust)

        target_shipping_fees = []
        for shipping_fee in cur_shipping_fees:
            per_item = round(float(shipping_fee['per_item']), 2)
            per_item += price_adjust
            target_shipping_fees.append({
                'per_order': shipping_fee['per_order'],
                'per_item': '%.2f' % per_item
            })

        shipping_fees = stm.get_shipping_fee()
        if shipping_fees:
            if shipping_fees == target_shipping_fees:
                shipping_adjust_recorder.record_shipping_ajust(shipping_fees)
                logger.info('Adjusted shipping fees: %s', str(shipping_fees))
            else:
                logger.warn(
                    'Adjusted shipping fees: %s, but target shipping fees are: %s',
                    shipping_fees, target_shipping_fees)
        else:
            logger.warn('Could not identify adjusted shipping fees')
    finally:
        driver.quit()


if __name__ == '__main__':
    update_shipping_price()

# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import sys
import datetime
import time

import click

from amazon_management import (
    logger,
    get_shared_driver,
    MARKETPLACE_MAPPING
)
from amazon_management.utils import YamlConfigLoader
from amazon_management.helpers import SellerLoginHelper
from amazon_management.payments_reports_manager import PaymentsReportsManager
from amazon_management.payments_reports_generation_recorder import PaymentsReportsGenerationRecorder


@click.command()
@click.option('-c', '--config_path', help='Configuration file path.')
def request_report(config_path):
    if not config_path:
        logger.error('config_path is required to run!')
        sys.exit(1)

    config_path = os.path.abspath(os.path.expanduser(config_path))
    if not os.path.isfile(config_path):
        logger.error('Could not find configuration file - %s', config_path)
        sys.exit(0)

    cl = YamlConfigLoader(config_path)
    config = cl.load()

    marketplace = config['account']['marketplace'].lower()
    email = config['account']['email']
    password = config['account']['password']

    now = datetime.datetime.utcnow()
    time_format = '%m/%d/%Y'

    payments_reports_generation_recorder = PaymentsReportsGenerationRecorder(marketplace)
    last_operate_time, params = payments_reports_generation_recorder.get_last_record()
    if last_operate_time is None:
        start_date_str = (now - datetime.timedelta(days=31)).strftime(time_format)
        end_date_str = (now - datetime.timedelta(days=1)).strftime(time_format)
    else:
        if last_operate_time.date() == now.date():
            logger.info(
                'Payments reports generation has already finished today - %s',
                repr(last_operate_time))
            sys.exit(0)

        last_end_date = datetime.datetime.strptime(params['end_date'], time_format)

        yesterday = now - datetime.timedelta(days=1)
        if last_end_date.date() >= yesterday.date():
            logger.info(
                'Lastest payments reports has already been generated - %s',
                repr(last_end_date))
            sys.exit(0)

        start_date_str = (last_end_date + datetime.timedelta(days=1)).strftime(time_format)
        end_date_str = yesterday.strftime(time_format)

    driver = get_shared_driver(marketplace)
    helper = SellerLoginHelper(driver, email, password, marketplace)

    try:
        generate_payments_reports_url_template = "https://{}/payments/reports/custom/request?tbla_daterangereportstable=sort:%7B%22sortOrder%22%3A%22DESCENDING%22%7D;search:undefined;pagination:1;"
        generate_payments_reports_url = generate_payments_reports_url_template.format(
            MARKETPLACE_MAPPING.get(marketplace)['sellercentral'])
        driver.get(generate_payments_reports_url)
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

            driver.get(generate_payments_reports_url)

        if not helper.pick_marketplace():
            logger.error('Could not pick marketplace, exit')
            sys.exit(1)

        driver.get(generate_payments_reports_url)

        payments_reports_manager = PaymentsReportsManager(driver)
        result = payments_reports_manager.request_report(start_date_str, end_date_str)
        if result:
            payments_reports_generation_recorder.record({
                'start_date': start_date_str,
                'end_date': end_date_str,
                'report_type': 'Transaction',
                'timeRangeType': 'Custom'
            })
        else:
            logger.error('Payments reports generation failed!')
    finally:
        driver.quit()


if __name__ == '__main__':
    request_report()

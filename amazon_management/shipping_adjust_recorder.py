# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import io
import json
import datetime

from amazon_management import shared_work_directory


class ShippingAdjustRecorder(object):
    def __init__(self, marketplace):
        self._marketplace = marketplace.lower()
        self._shipping_adjust_records_path = os.path.join(
            shared_work_directory, 'shipping',
            '{}_shipping_adjust_records.txt'.format(self._marketplace))
        self._time_format = '%Y%m%dT%H%M%S.%f'

    def record_shipping_ajust(self, shipping_fees):
        adjust_time = self.format_time(datetime.datetime.now())
        with io.open(
            self._shipping_adjust_records_path, 'a', encoding='utf-8', errors='ignore') as fh:
            record = json.dumps({'adjust_time': adjust_time, 'shipping_fees': shipping_fees})
            record += '\n'
            fh.write(record)

    def get_last_adjust_record(self):
        result = (None, None)

        if not os.path.isfile(self._shipping_adjust_records_path):
            return result

        with io.open(self._shipping_adjust_records_path, encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()
            last_record_str = None
            while not last_record_str:
                last_record_str = lines.pop()
            last_record = json.loads(last_record_str)
            last_adjust_time = self.deformat_time(last_record.get('adjust_time'))
            shipping_fees = last_record.get('shipping_fees')
            result = (last_adjust_time, shipping_fees)

        return result

    def is_shipping_adjusted(self, adjust_time):
        if adjust_time is None:
            return False

        now = datetime.datetime.now()
        return now.hour == adjust_time.hour

    def format_time(self, t):
        return t.strftime(self._time_format)

    def deformat_time(self, t_str):
        return datetime.datetime.strptime(t_str, self._time_format)

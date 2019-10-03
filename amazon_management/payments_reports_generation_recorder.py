# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import io
import json
import datetime

from amazon_management import shared_work_directory


class PaymentsReportsGenerationRecorder(object):
    def __init__(self, marketplace):
        self._marketplace = marketplace.lower()
        self._payments_report_generation_records_path = os.path.join(
            shared_work_directory, 'payments_reports', marketplace, 'generation_records.txt')
        records_dir = os.path.dirname(self._payments_report_generation_records_path)
        if not os.path.isdir(records_dir):
            os.makedirs(records_dir)

        self._time_format = '%Y%m%dT%H%M%S.%f'

    def record(self, operation_details):
        operation_time = self.format_time(datetime.datetime.now())
        with io.open(
            self._payments_report_generation_records_path,
            'a', encoding='utf-8', errors='ignore') as fh:
            params = dict(operation_details)
            params['time'] = operation_time
            record = json.dumps(params)
            record += '\n'
            fh.write(record)

    def get_last_record(self):
        result = (None, None)

        if not os.path.isfile(self._payments_report_generation_records_path):
            return result

        with io.open(
            self._payments_report_generation_records_path, encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()
            last_record_str = None
            while not last_record_str:
                last_record_str = lines.pop()
            last_record = json.loads(last_record_str)
            last_record_time = self.deformat_time(last_record.pop('time'))
            result = (last_record_time, last_record)

        return result

    def format_time(self, t):
        return t.strftime(self._time_format)

    def deformat_time(self, t_str):
        return datetime.datetime.strptime(t_str, self._time_format)

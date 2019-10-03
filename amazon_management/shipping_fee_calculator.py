# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import datetime


class ShippingFeeCalculator(object):
    def __init__(self, shipping_rule):
        self._shipping_rule = shipping_rule.copy()
        self._increase_hours = [int(hour_str.strip()) for hour_str in \
            shipping_rule.get('increase_hours', '').split(',') if hour_str.strip()]
        self._increase_amount = shipping_rule['increase_amount']
        self._decrease_hours = [int(hour_str.strip()) for hour_str in \
            shipping_rule.get('decrease_hours', '').split(',') if hour_str.strip()]
        self._decrease_amount = -shipping_rule['decrease_amount']

    def get_price_adjustment(self):
        hour = self.get_coordinate_hour()
        if hour in self._increase_hours:
            adjustment = self._increase_amount
        elif hour in self._decrease_hours:
            adjustment = self._decrease_amount
        else:
            adjustment = 0

        return adjustment

    def get_coordinate_hour(self):
        utc_now = datetime.datetime.utcnow()
        coordinate_time = utc_now - datetime.timedelta(hours=7)

        return coordinate_time.hour

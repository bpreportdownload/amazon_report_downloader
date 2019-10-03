# -*- coding: utf-8 -*-

# Copyright © 2018 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from datetime import datetime

from amazon_management.shipping_adjust_recorder import ShippingAdjustRecorder

def test_time_formation():
    recorder = ShippingAdjustRecorder('')
    now = datetime.now()
    formatted_time = recorder.format_time(now)
    deformatted_time = recorder.deformat_time(formatted_time)
    assert now == deformatted_time

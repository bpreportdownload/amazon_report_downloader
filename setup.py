# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from setuptools import setup, find_packages
from os import path
import io

here = path.abspath(path.dirname(__file__))

try:
    with io.open(path.join(here, 'README.md'), encoding='utf-8', errors='ignore') as f:
        long_description = f.read()
except:
    long_description = ''

with open(path.join(here, 'amazon_management', 'VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

with open(path.join(here, 'requirements.txt')) as f:
    requirements = []
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name='amazon_management',
    version=version,
    description='Amazon seller management tool.',
    long_description=long_description,
    url='https://bitbucket.org/sfds-dev/amazon-management',
    author='Neal Wong',
    author_email='neal.wkacc@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords='amazon seller management',
    packages=find_packages(exclude=('tests')),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'upload=amazon_management.bin.upload_files:upload',
            'download_report=amazon_management.bin.download_report:download_report',
            'clear_inv_by_sku=amazon_management.bin.clear_inv_by_sku:clear_inv_by_sku',
            'update_shipping_price=amazon_management.bin.update_shipping_price:update_shipping_price',
            'generate_financial_transactions=amazon_management.bin.generate_financial_transactions:request_report'
        ]
    }
)

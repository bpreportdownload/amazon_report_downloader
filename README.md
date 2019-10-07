amazon_management
=====================

Amazon seller central management helper tools.

* clear_inv_by_sku - Delete inventory records by search sku keywords.
* update_shipping_price - Update shipping price by shipping template name
* generate_financial_transactions - Generate payments reports of report type _GET_DATE_RANGE_FINANCIAL_TRANSACTION_DATA_

开发流程
-------------

1. 获取项目代码

2. 进入项目目录，使用 
```pip install -e . ``` 
打包安装在本地机器上，运行相应的命令查看效果

3. 添加新的命令需要放在 amazon_management/bin下



Installation
-------------

The simplest way is to install it via `devpi`:

    devpi install amazon_management

To upgrade, use:

    devpi install amazon_management


Run
-------------

```
clear_inv_by_sku --help
```
```
update_shipping_price --help
```
```
generate_financial_transactions --help
```

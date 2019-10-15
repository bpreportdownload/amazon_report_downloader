from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

# setting up chromedriver and configuring path automatically using webdriver-manager
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://sellercentral.amazon.com/")
time.sleep(random.randint(1, 7))

# login
driver.find_element_by_xpath('//*[@id="sign-in-button"]/button').click()
username = driver.find_element_by_id('ap_email')
password = driver.find_element_by_id("ap_password")
username.send_keys("LILIINEUFRATEN@GMAIL.COM")
password.send_keys("youcandoit!@")
time.sleep(random.randint(1, 7))
driver.find_element_by_id("signInSubmit").click()
time.sleep(30)
# 移动鼠标到inventory
inventory = driver.find_element_by_id("sc-navtab-inventory")
webdriver.ActionChains(driver).move_to_element(inventory).perform()
time.sleep(random.randint(1, 7))

driver.find_element_by_xpath('//*[@id="sc-navtab-inventory"]/ul/li[7]/a').click()
time.sleep(random.randint(1, 7))

# click inventory report

driver.find_element_by_id("a-autoid-0-announce").click()
time.sleep(random.randint(1, 7))
driver.find_element_by_id("dropdown1_0").click()
time.sleep(random.randint(1, 7))
driver.find_element_by_xpath('//*[@id="a-autoid-5"]/span/input').click()
time.sleep(random.randint(10, 20))
driver.refresh()

# download
time.sleep(random.randint(1, 7))
driver.find_element_by_xpath('//*[@id="50002018176-report_download"]/div/a').click()
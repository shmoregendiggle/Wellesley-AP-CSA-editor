from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def waitFor(clasString, selector):
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((selector, clasString))
    )
    return driver.find_element(selector, clasString)

def getToken(username, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    global driver
    driver = webdriver.Chrome(options=options)
    driver.get("https://wellesley.instructure.com/profile/settings")
    driver.find_element("name", "pseudonym_session[unique_id]").send_keys(username)
    driver.find_element("name", "pseudonym_session[password]").send_keys(password)
    driver.find_element("name", "commit").click()
    waitFor(".btn.btn-primary.add_access_token_link", "css selector").click()
    waitFor("access_token[purpose]", "name").send_keys("CSAIDE")
    waitFor(".btn.btn-primary.submit_button.button_type_submit.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-only", "css selector").click()
    time.sleep(1)
    return waitFor(".visible_token", "css selector").get_attribute("innerHTML")

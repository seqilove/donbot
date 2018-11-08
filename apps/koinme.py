import datetime
import json
import sys
import time

from selenium.common.exceptions import (
    NoSuchElementException, NoSuchWindowException, WebDriverException, TimeoutException, UnexpectedAlertPresentException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

# sys.path.append(sys.path[0] + "/..")
from apps.seletask import SeleTask, new_windows_opened
from utils.telegram import get_tg


class Koinme(SeleTask):

    urls = {
        'home': 'http://koinme.com/',
        'login': 'http://koinme.com/sign-in',
        'offers': 'http://koinme.com/offers',
        'refer': 'http://koinme.com/refer-earn'
    }

    def __init__(self, config):
        super().__init__(config)

    def get_task_name(self):
        task_name = []
        task_name.append(self.task)
        task_name.append(self.extra.get('username'))
        _config = self.extra.get('config')
        if _config:
            task_name.append(_config)
        if self._config.get('prefs'):
            _proxy = self._config['prefs'].get('network.proxy.socks')
            if _proxy:
                task_name.append(_proxy)
            else:
                task_name.append('noproxy')
        else:
            task_name.append('noproxy')
        task_name = '-'.join(task_name)
        return task_name

    def run(self):
        self.koinme()

    def koinme(self, auto=False):
        offers_h, offer_h = None, None
        last_t = None
        _alert_exist = False
        wait = 240

        while True:
            try:
                if _alert_exist:
                    _alert_exist = False
                    self.s.close_alert()
                    continue

                if offers_h is None:
                    if offer_h is None:
                        if self.s.driver is None:
                            self.s.start()

                        offers_h = self.s.driver.window_handles[0]
                        # offers_h = self.s.get_new_window()
                    else:
                        self.s.driver.switch_to.window(self.s.driver.window_handles[0])
                        offers_h = self.s.get_new_window()
                    continue
                else:
                    # if not self.check_offers_url(offers_h):
                    #     continue
                    try:
                        try:
                            self.s.driver.switch_to.window(offers_h)
                        except NoSuchWindowException:
                            offers_h = None
                            continue
                        if self.s.driver.current_url != self.urls['offers']:
                            self.visit_offers_page()

                        if offer_h is None:
                            try:
                                _windows = self.s.driver.window_handles
                                offer = self.s.find_element((By.XPATH, '//a[@class="start-offer"]/img'))
                                # offer.click()
                                self.s.driver.execute_script("arguments[0].click();", offer)
                                # del offer
                                last_t = None
                                _new_open_windows = self.s.wait().until(new_windows_opened(_windows))
                                if _new_open_windows:
                                    offer_h = _new_open_windows[0]
                            except (NoSuchElementException, TimeoutException) as e:
                                time.sleep(10)
                                try:
                                    info = self.s.driver.find_element(By.XPATH, '//h3')
                                    # info = self.s.driver.find_element(By.XPATH, '//div#pjbox/h3')
                                    info_text = info.get_attribute('innerText')
                                except (NoSuchElementException, TimeoutException) as e:
                                    info_text = 'No offers found!'
                                self.logger.debug(info_text)
                                self.logger.debug('wait %s seconds', 30 * 60)
                                time.sleep(30 * 60)
                            continue
                        else:
                            try:
                                try:
                                    self.s.driver.switch_to.window(offer_h)
                                except NoSuchWindowException:
                                    offer_h = None
                                    continue

                                if self.s.driver.current_url == self.urls['offers']:
                                    self.visit_offers_page()
                                    try:
                                        offer = self.s.driver.find_element(By.XPATH, '//a[@class="start-offer"]/img')
                                        self.s.close_handles(self.s.driver.window_handles, exclude=[offers_h, offer_h])
                                        # offer.click()
                                        self.s.driver.execute_script("arguments[0].click();", offer)
                                        last_t = None
                                        self.logger.debug('wait 60 seconds')
                                        time.sleep(60)
                                    except (NoSuchElementException, TimeoutException):
                                        time.sleep(10)
                                        try:
                                            info = self.s.driver.find_element(By.XPATH, '//h3')
                                            # info = self.s.driver.find_element(By.XPATH, '//div#pjbox/h3')
                                            info_text = info.get_attribute('innerText')
                                        except NoSuchElementException as e:
                                            info_text = 'No offers found!'
                                        self.logger.debug(info_text)
                                        self.logger.debug('wait %s seconds', 30 * 60)
                                        time.sleep(30 * 60)
                                    continue
                                else:
                                    if auto:
                                        self.logger.debug('wait %s seconds', wait)
                                        time.sleep(wait)
                                    else:
                                        try:
                                            self.s.driver.find_element(By.ID, 'clock')
                                        except (NoSuchElementException, TimeoutException):
                                            self.s.driver.refresh()
                                            last_t = None
                                            time.sleep(10)
                                            continue
                                        try:
                                            more = self.s.driver.find_element(By.LINK_TEXT, 'Earn 1.00 More Koins')
                                            # more.click()
                                            self.s.driver.execute_script("arguments[0].click();", more)
                                            self.logger.debug('Get 1 koins, start next')
                                            last_t = datetime.datetime.now()
                                            self.logger.debug('wait %s seconds', wait)
                                            time.sleep(wait)
                                        except (NoSuchElementException, TimeoutException):
                                            if last_t is None:
                                                last_t = datetime.datetime.now()
                                                self.logger.debug('wait %s seconds', wait)
                                                time.sleep(wait)
                                            else:
                                                _duration = (datetime.datetime.now() - last_t).total_seconds()
                                                if _duration > 900:
                                                    self.s.driver.refresh()
                                                    last_t = None
                                                else:
                                                    self.logger.debug('wait 60 seconds')
                                                    time.sleep(60)
                            except NoSuchWindowException as e:
                                time.sleep(5)
                                offer_h = None
                                continue
                    except NoSuchWindowException as e:
                        time.sleep(5)
                        # offers_h = self.s.get_new_window()
                        offers_h = None
                        continue

            except KeyboardInterrupt:
                self.s.kill()
                offers_h, offer_h = None, None
                raise
            except (ConnectionRefusedError) as e:
                self.logger.exception(e)
                time.sleep(5)
                self.s.kill(profile_persist=True)
                offers_h, offer_h = None, None
                time.sleep(5)
            except UnexpectedAlertPresentException as e:
                _alert_exist = True
            except (TimeoutException, NoSuchWindowException, WebDriverException) as e:
                b = (
                    'Failed to decode response from marionette',
                    'Failed to write response to stream',
                    'Tried to run command without establishing a connection',
                )
                if e.msg in b:
                    self.logger.exception(e)
                    time.sleep(5)
                    self.s.kill()
                    offers_h, offer_h = None, None
                    time.sleep(5)
                else:
                    self.logger.exception(e)
                    time.sleep(5)
                    offers_h, offer_h = None, None
                    last_t = None
            except Exception as e:
                self.logger.exception(e)
                time.sleep(5)
                offers_h, offer_h = None, None
                last_t = None

    def add_cookie(self):
        cookies = None
        if self.cookie_path.exists():
            with open(self.cookie_path, 'r') as fp:
                try:
                    cookies = json.load(fp)
                except json.JSONDecodeError:
                    self.delete_cookie()
        if cookies:
            for c in cookies:
                if c.get('domain').startswith('.'):
                    c['domain'] = c['domain'].split('.', 1)[-1]
                self.s.driver.add_cookie(c)

    def save_cookie(self):
        cookies = self.s.driver.get_cookies()
        print(cookies)
        # cookies = [c for c in cookies if 'alexamaster.net' in c.get('domain')]
        with open(self.cookie_path, 'w') as fp:
            try:
                json.dump(cookies, fp)
            except Exception:
                pass

    def visit_offers_page(self):
        self.s.get(self.urls['offers'])
        time.sleep(5)
        logged = False
        login_action = False
        while not logged:
            if self.s.driver.current_url == self.urls['offers']:
                logged = True
                if login_action:
                    self.save_cookie()
            else:
                login_action = False
                self.add_cookie()
                self.s.get(self.urls['offers'])
                time.sleep(5)
                if self.s.driver.current_url == self.urls['offers']:
                    logged = True
                else:
                    self.delete_cookie()
                    self.login()
                    login_action = True
                    self.s.get(self.urls['offers'])
                    time.sleep(5)

    def login(self):
        try:
            tg = get_tg()
            if tg:
                tg.send_message('saythx', 'please solve login captcha')
            if self.s.driver.current_url != self.urls['login']:
                self.s.get(self.urls['login'])
            username = self.s.find_element((By.ID, 'loginform-username'))
            self.s.clear(username)
            username.send_keys(self.extra['username'])
            password = self.s.driver.find_element(By.ID, 'loginform-password')
            self.s.clear(password)
            password.send_keys(self.extra['password'])
            while True:
                _input = input('Login(Please enter "y" "yes" "ok" "n" "no" or "retry")?')
                if _input.isalpha():
                    if _input.lower() in ['y', 'yes', 'ok']:
                        self.logger.debug('Login success')
                        break
                    elif _input.lower() in ['n', 'no']:
                        self.logger.debug('Login failed')
                        raise WebDriverException('login failed')
                    elif _input.lower() in ['retry']:
                        self.logger.debug('Retry')
                        time.sleep(10)
                        raise WebDriverException('retry login koinme')
        except WebDriverException as e:
            if e.msg in ['retry login koinme']:
                self.s.get('about:blank')
                time.sleep(3)
                self.login()
            else:
                raise e
        # cookies = self.s.driver.get_cookies()
        # self.cookies = self.s.driver.get_cookies()
        # cookies = [c for c in cookies if 'koinme.com' in c.get('domain')]
        # self.cookies = [c for c in self.cookies if 'koinme.com' in c.get('domain')]

    def check_offers_url(self, offers_h):
        result = False
        try:
            self.s.driver.switch_to.window(offers_h)
            if self.s.driver.current_url != self.urls['offers']:
                self.visit_offers_page()
            result = True
        except NoSuchWindowException as e:
            time.sleep(5)
            offers_h = self.s.get_new_window()
            result = False
        except Exception as e:
            raise e

        return result


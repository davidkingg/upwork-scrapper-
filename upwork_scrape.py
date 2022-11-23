import feedparser
import pandas as pd
import time
import warnings
from bs4 import BeautifulSoup
from random import randint
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from apscheduler.schedulers.background import BackgroundScheduler


warnings.filterwarnings('ignore')
username = 'kingunilag@gmail.com'
password = 'Handsome5'


def ScrappingRandomUa():
    try:
        selected_ua = "?"
        ua_lists = []
        ua_lists.append(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")
        ua_lists.append(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")
        ua_lists.append(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")
        total = len(ua_lists)
        rand_num = randint(0, total - 1)
        selected_ua = ua_lists[rand_num].strip()
        return selected_ua
    except:
        print("[-] Problem in RandomUA")
        pass


def browser():
    ua = "?"
    ua = ScrappingRandomUa()
    options = webdriver.ChromeOptions()
    d = DesiredCapabilities.CHROME
    d['goog:loggingPrefs'] = {'browser': 'ALL'}
    options.add_argument('--no-sandbox')
    options.add_argument('--user-agent=' + ua)
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("disable-infobars")
    options.add_argument('--disable-extensions')
    # options.add_argument('--headless')
    options.add_argument("--window-size=1280,800")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--no-default-browser-check")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--no-first-run")
    options.add_argument("--disable-blink-features")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-default-apps")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", {"profile.allow_all_cookies": True})
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 0})
    options.add_experimental_option("prefs", {"profile.cookie_controls_mode": 0})

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.maximize_window()
    driver.get('https://www.upwork.com/ab/account-security/login')
    time.sleep(4)

    for y in username:
        driver.find_element("xpath", '//input[@id="login_username"]').send_keys(y)
        time.sleep(2)
    time.sleep(3)
    driver.find_element("xpath", '//button[@id="login_password_continue"]').click()
    time.sleep(50) #time to solve captcha
    for y in password:
        time.sleep(2)
        driver.find_element("xpath", '//input[@id="login_password"]').send_keys(y)
    time.sleep(3)
    driver.find_element("xpath", '//button[@id="login_control_continue"]').click()
    time.sleep(3)
    time.sleep(10)
    print('initiated browser ...')
    return driver


def scrape(driver, url):
    driver.get(url)
    time.sleep(3)
    try:
        driver.find_element("xpath", '//button[@data-cy="close-button"]').click()
        time.sleep(3)
    except:
        pass

    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    title = soup.findAll("header", {"class": "up-card-header d-flex"})[0].text.lstrip().rstrip()

    about_client = \
        [x.text.lstrip().rstrip() for x in soup.findAll("ul", {"class": "cfe-ui-job-about-client-visitor"})[0:1]][
            0].split(
            '\n')

    country = about_client[0] + ' ' + about_client[1].lstrip().rstrip()
    jobs_posted = [x for x in about_client if ' jobs posted' in x][0].lstrip().rstrip()
    hire_rate = [x for x in about_client if ' hire rate' in x][0].lstrip().rstrip()
    try:
        total_spent = [x for x in about_client if '$' in x][0].lstrip().rstrip()
    except:
        total_spent = '$0'
    try:
        hires = [x for x in about_client if 'hires' in x][0].lstrip().rstrip()
    except:
        hires = '0'
    try:
        hourly_rate = [x for x in about_client if 'avg hourly rate paid' in x][0].lstrip().rstrip()
    except:
        hourly_rate = '$0'

    try:
        driver.find_element("xpath", '//h4[@data-cy="jobs-in-progress-button"]').click()
    except:
        pass
    progresses = driver.find_elements_by_xpath('//div[@data-cy="job"]')
    if len(progresses) == 0:
        res = pd.DataFrame([[title, country, jobs_posted, hire_rate, total_spent, hires, hourly_rate]],
                           columns=['title', 'country', 'jobs_posted', 'hire_rate', 'total_spent', 'hires',
                                    'hourly_rate'])
        res.to_excel('test_upwork2.xlsx', index=False)
        return res
    res = pd.DataFrame(
        columns=['title', 'country', 'jobs_posted', 'hire_rate', 'total_spent', 'hires', 'hourly_rate', 'job_title',
                 'job_status', 'freelancer', 'job_duration', 'job_price'])
    for i in range(len(progresses)):
        if i != 0:
            title, country, jobs_posted, hire_rate, total_spent, hires, hourly_rate = '', '', '', '', '', '', ''
        progress = progresses[i].text.split('\n')
        job_title = progress[0]
        try:
            job_status = [x for x in progress if 'Job in progress' in x][0]
        except:
            job_status = 'Completed'
        freelancer = [x for x in progress if 'reelancer' in x][0].split('reelancer')[1].replace(': ', '').lstrip()
        job_duration = [x for x in progress if ' - ' in x][0]
        try:
            job_price = [x for x in progress if 'Fixed-price' in x][0]
        except:
            job_price = [x for x in progress if 'hrs' in x][0]
        res = res.append(pd.DataFrame([[title, country, jobs_posted, hire_rate, total_spent, hires, hourly_rate,
                                        job_title, job_status, freelancer, job_duration, job_price]],
                                      columns=res.columns))
        res.to_excel('test_upwork2.xlsx', index=False)
        return res


def get_feeds():
    try:
        df = pd.read_excel('feed_links.xlsx')
    except:
        df = pd.DataFrame(columns=['link'])
    links = []
    titles = []
    scrape_links = []
    for i in range(2):
        d = feedparser.parse(
            f'https://www.upwork.com/ab/feed/jobs/rss?q=python%20aws&sort=recency&paging={i}%3B50&api_params=1')
        time.sleep(2)
        for x in d['entries']:
            links.append(x.link)
            titles.append(x.title)
            if x.link not in set(df['link']):
                if len(df) != 0:
                    scrape_links.append(x.link)
    pd.DataFrame({'title': titles, 'link': links}).to_excel('feed_links.xlsx', index=False)
    return scrape_links


driver = browser()


def action():
    links = get_feeds()
    if links:
        for url in links:
            scrape(driver, url)
    else:
        print('No new links added')


action()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(action, 'interval', minutes=5)
    scheduler.start()
    # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

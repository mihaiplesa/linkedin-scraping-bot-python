#!/usr/bin/env python3

import argparse
import json
from time import sleep
from random import randint
from datetime import datetime
from splinter import Browser

DATE_FORMAT = '%Y%m%d'

def login(browser, username, password):
    browser.visit('https://www.linkedin.com/')
    browser.fill('session_key', username + '\n')
    browser.fill('session_password', password + '\n')


def logout(browser):
    browser.visit('https://www.linkedin.com/m/logout')
    sleep(3)


def search_people(browser, query):
    browser.is_element_present_by_tag('input', wait_time=10)
    browser.find_by_tag('input').first.fill(query + '\n')
    browser.is_element_present_by_text('People', wait_time=10)
    browser.find_by_text('People').first.click()
    # browser.is_element_present_by_css('.search-result__result-link .ember-view', wait_time=10)    
    # browser.find_by_text('2nd').first.click()
    return browser.driver.current_url + '&facetNetwork=%5B"S"%2C"O"%5D&page='


def extract_people(browser, people_url, page_no):
    browser.visit(people_url + str(page_no))
    browser.is_element_present_by_css('.search-result__result-link .ember-view', wait_time=10)
    browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    browser.is_element_present_by_css('.next', wait_time=10)
    print(len(browser.find_by_css('.search-result__info')))
    # sleep(2)
    people = {}
    for elem in browser.find_by_css('.search-result__info'):
        browser.is_element_present_by_tag('a', wait_time=10)
        people[elem.find_by_tag('a').first['href']] = None
    return people


def visit_people(browser, people, days):
    now = datetime.now()
    c = 0
    for url, date in people.items():
        if not date or (date and (now - datetime.strptime(date, DATE_FORMAT)).days > days):
            print(str(c) + ' visiting ' + url + ' ' + str(date))            
            browser.visit(url)
            browser.is_element_present_by_id('profile-wrapper', wait_time=10)
            browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")            
            people[url] = now.strftime(DATE_FORMAT)
            sleep(randint(2, 6))
            c += 1
    return people


parser = argparse.ArgumentParser()
parser.add_argument('--username', default='')
parser.add_argument('--password', default='')
parser.add_argument('--extract', required=False)
parser.add_argument('--visit', required=False)
parser.add_argument('--file', default='db.json')
parser.add_argument('--from', type=int, default=1)
parser.add_argument('--no', type=int, default=1)
args = parser.parse_args()

people = {}
try:
    with open(args.file, 'r') as f:
        people = json.loads(f.read())
except Exception as ex:
    pass
print(len(people))

try:
    with Browser('chrome') as browser:
        if args.extract:
            login(browser=browser, username=args.username, password=args.password)
            print('extracting ' + str(args.no) + ' pages')
            people_url = search_people(browser=browser, query=args.extract)
            for page_no in range(1, args.no + 1):
                print(page_no)
                new_people = extract_people(browser=browser, people_url=people_url, page_no=page_no)
                print(new_people)
                people.update({url: date for url, date in new_people.items() if url not in people})
                if not new_people:
                    break
            logout(browser=browser)            
        elif args.visit:
            login(browser=browser, username=args.username, password=args.password)
            people = visit_people(browser=browser, people=people, days=args.no)
            logout(browser=browser)    
finally:
    print(len(people))
    with open(args.file, 'w') as f:
        f.write(json.dumps(people))

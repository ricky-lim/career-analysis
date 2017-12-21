#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup

CHROME_DRIVER = "/usr/local/bin/chromedriver"


def open_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(CHROME_DRIVER, chrome_options=chrome_options)


def parse_salary_table(table):
    """
    parse HTML table (row x 2 columns, i.e, job_title and salary) into a list of dicts with keys correspond to columns
    :param table: salary HTML table from glassdoor
    <tr>
        <td class="job_title"><a href="..." title="...">Onderzoeker - per maand bij Philips</a></td>
        <td class="salary">€ 4.396/mnd</td>
    </tr>
    :return:
    [{"job_title": "Onderzoeker - per maand bij Philips",
      "salary": "€ 4.396/mnd"}]
    """
    res_all = []
    for s in table:
        res = {"job_title": s.find("td", {"class": "job_title"}).find("a").string,
               "salary": s.find("td", {"class": "salary"}).string}
        res_all.append(res)
    return res_all


def get_next(html_soup):
    for l in html_soup.find_all("link", {"rel": True, "href": True}):
        if "next" in l.get("rel"):
            return l.get("href")


def get_salary_per_page(website):
    """

    :param website: string url
    e.g "https://www.glassdoor.com/Salaries/netherlands-onderzoeker-salary-SRCH_IL.0,11_IN178_KO12,23_SDMC.htm"
    :return: a tuple of ( [dict of parsed salary table per page, string website for the next page otherwise None )
    e.g ([{"job_title": "hello", "salary": "0"}], "www.glassdoor.com/next")
    """
    browser = open_chrome()
    browser.get(website)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    salary_table = soup.find(id="SalarySearchResults").find("div", class_="dataTableModal"). \
        find("tbody").find_all("tr")

    return parse_salary_table(salary_table), get_next(soup)


def get_all_salaries(website):
    """
    paginate through the page to get all the salary
    :param website: string website
    :return: a list of parsed salaries
    e.g:  [{'job_title': 'Onderzoeker Stagiair - per maand bij TNO',
            'salary': '€ 492/mnd'},
           {'job_title': 'Onderzoeker - per maand bij Philips',
            'salary': '€ 4.396/mnd'}, ...]
    """

    has_visited = []
    res, next_page = get_salary_per_page(website)
    while next_page:
        next_res, next_page = get_salary_per_page(next_page)
        if next_page in has_visited:
            break
        has_visited.append(next_page)
        res.extend(next_res)
    return res

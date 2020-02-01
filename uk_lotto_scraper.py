"""
    File name: uk_lotto_scraper.py
    Author: Matthew Carter
    Date created: 26/12/2019
    Date last modified: 31/01/2020
    Python Version: 3.7.6

    Note: Only used for educational purposes.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pandas as pd

# Create list of urls from which results need to be obtained. At time of writing, format of website URL is
# https://www.lottery.co.uk/lotto/results/archive-2015 . New 1-59 ball format lotto applies from 8th October 2015 to
# the present.
url_list = []
years = [2015, 2016, 2017, 2018, 2019, 2020]
for year in years:
    url_list.append("https://www.lottery.co.uk/lotto/results/archive-{}".format(year))

# Scrape the lotto results from each url and store them in a dictionary.
lotto_results_dict = {}
for url in url_list:
    # Get the HTML contents of the page.
    page = requests.get(url)
    # Use BeautifulSoup to parse the HTML.
    soup = BeautifulSoup(page.content, 'html.parser')
    # Lotto draw results are stored in a table on the page.
    results_table = soup.find('table', {'class': 'table lotto mobFormat'})
    all_rows = results_table.find_all('tr')
    # Loop over all rows in the results table apart from first row which is the header.
    for row in all_rows[1:]:
        # Get all cells in the row.
        all_cells = row.find_all('td')
        # Get draw date from first cell in row (position 0). Use regular expression to isolate the date from string and
        # format it ready for use in a DataFrame.
        date_text_full = all_cells[0].find('a').text
        date_text = re.sub(r'([0-3]?[0-9])(st|nd|rd|th)', r'\1', date_text_full)
        date_datetime = datetime.strptime(date_text, '%A %d %B %Y').date()
        print(date_datetime)
        # Get the six main balls drawn from second cell in row (position 1).
        main_balls_list = []
        main_balls = all_cells[1].find_all('div', {'class': 'result small lotto-ball'})
        for ball in main_balls:
            ball_int = int(ball.text)
            main_balls_list.append(ball_int)
        print(*main_balls_list, sep=", ")
        # Get the bonus ball drawn, also from second cell in row (position 1).
        bonus_ball = all_cells[1].find('div', {'class': 'result small lotto-bonus-ball'})
        bonus_ball_int = int(bonus_ball.text)
        print(bonus_ball_int)
        # Add the draw date and balls to the results dictionary.
        lotto_results_dict[date_datetime] = [main_balls_list, bonus_ball_int]
        print("------------------")

# Create a DataFrame from the results dictionary and save to a CSV file.
lotto_results_df = pd.DataFrame.from_dict(lotto_results_dict, orient='index',
                                          columns=["main_balls", "bonus_ball"]).rename_axis('draw_date').reset_index()
lotto_results_df.to_csv("lotto_results.csv", index=False)

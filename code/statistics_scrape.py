## NBA Stats Scraper
# Append to current data

##### BIGGER PICTURE: NEED A TEXT FILE OR SOME MASTER FILE THAT WE CAN
##### ADD DATES TO SO WE DON'T HAVE TO HARD CODE THE SEASON WE'RE IN

### WHAT ABOUT HEADLESS? IT WOULDN'T WORK
# https://github.com/SeleniumHQ/selenium/issues/4477

import re
from selenium import webdriver
import datetime
from random import uniform
from time import sleep
import pandas as pd


def nba_season_stats(to_yesterday = True,
                    season = "2021-22",
                    all = False,
                    chrome_path = '/Users/TeddyEinsidler/Desktop/chromedriver'):


    if all or season == "ALLTIME":
        url = f"https://www.nba.com/stats/players/boxscores/?Season=ALLTIME&SeasonType=Regular%20Season"

    elif not re.match("\d{4}\-\d{2}", season):
        print("""
        The season string is not properly formatted.
            How to format: '1946-47', '1979-80', '2002-03'
            For all seasons: 'ALLTIME' or set all = True
        """)
    elif (int(season[-2:]) - int(season[2:4]) != 1) or (int(season[:4]) < 1946):
        print("""
        Make sure the string is for a single season and not before 1946.
            How to format: '1946-47', '1979-80', or '2002-03'
            For all seasons: 'ALLTIME' or set all = True
        """)
    elif to_yesterday:
        yesterday = (datetime.date.today() - datetime.timedelta(days = 1))
        url = f"https://www.nba.com/stats/players/boxscores/?Season={season}&SeasonType=Regular%20Season&DateTo={yesterday.month}%2F{yesterday.day}%2F{yesterday.year}"
    else:
        url = f"https://www.nba.com/stats/players/boxscores/?Season={season}&SeasonType=Regular%20Season"

    driver = webdriver.Chrome(executable_path=chrome_path)


    # Set a wait time
    driver.implicitly_wait(10)
    driver.get(url)

    # Locate the table
    table = driver.find_element_by_class_name('nba-stat-table__overflow').text.split('\n')

    # Next page arrow
    next_page = driver.find_elements_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[3]/div/div/a[2]')

    # Number of clicks is one less than the number of pages
    n_page = int(driver.find_element_by_class_name("stats-table-pagination__info").text.split('\n')[-1].strip(" of "))
    n_clicks = n_page - 1


    # Initialize an empty list for the players' names and their stats to append
    player_names = []
    player_stats = []

    # Loop through n_clicks times
    for _ in range(n_clicks):

        # Define the table we are scraping from
        table = driver.find_element_by_class_name('nba-stat-table__overflow').text.split('\n')

        # Iterate through the stats table to append to the two player lists
        for num, info in enumerate(table):
            if num == 0:
                continue
            else:
                if num % 2 == 1:
                    player_names.append(info)
                if num % 2 == 0:
                    player_stats.append([i for i in info.split(' ')])

        # Click to next page
        driver.execute_script("arguments[0].click();", next_page[0])

        # Pause for uniformly random amounts of seconds
        sleep(uniform(0.5, 1.5) * 4)

    # Return a DataFrame from the lists
    return pd.DataFrame({'Player': player_names,
                  'Team': [i[0] for i in player_stats],
                  'Match-up': [i[2]+i[3] for i in player_stats],
                  'Date': [i[4] for i in player_stats],
                  'W/L': [i[5] for i in player_stats],
                  'Min': [i[6] for i in player_stats],
                  'Pts': [i[7] for i in player_stats],
                  'FGM': [i[8] for i in player_stats],
                  'FGA': [i[9] for i in player_stats],
                  'FG%': [i[10] for i in player_stats],
                  '3PM': [i[11] for i in player_stats],
                  '3PA': [i[12] for i in player_stats],
                  '3P%': [i[13] for i in player_stats],
                  'FTM': [i[14] for i in player_stats],
                  'FTA': [i[15] for i in player_stats],
                  'FT%': [i[16] for i in player_stats],
                  'OREB': [i[17] for i in player_stats],
                  'DREB': [i[18] for i in player_stats],
                  'REB': [i[19] for i in player_stats],
                  'AST': [i[20] for i in player_stats],
                  'STL': [i[21] for i in player_stats],
                  'BLK': [i[22] for i in player_stats],
                  'TOV': [i[23] for i in player_stats],
                  'PF': [i[24] for i in player_stats],
                  '+/-': [i[25] for i in player_stats]})


def nba_defense(season_year,
                chrome_path = '/Users/TeddyEinsidler/Desktop/chromedriver'):

    driver = webdriver.Chrome(executable_path=chrome_path)

    driver.implicitly_wait(10)

    # URL
    url = f'https://www.nba.com/stats/teams/defense/?sort=W&dir=-1&Season={season_year}&SeasonType=Regular%20Season'

    driver.get(url)


    # location of table, button to click to next page
    table = driver.find_element_by_class_name('nba-stat-table__overflow').text.split('\n')

    # empty lists to append to
    teams = []
    team_stats = []

    # find locations of team names and team stats
    for num, info in enumerate(table):
        if num > 8:
            if num % 3 == 0:
                teams.append(info)
            if (num -1) % 3 == 0:
                team_stats.append([i for i in info.split(' ')])

    # return dataframe
    return pd.DataFrame({
        'Season': season_year,
        'Team': teams,
        'GP': [i[0] for i in team_stats],
        'W': [i[1] for i in team_stats],
        'L': [i[2] for i in team_stats],
        'MIN': [i[3] for i in team_stats],
        'DEF_RTG': [i[4] for i in team_stats],
        'DREB': [i[5] for i in team_stats],
        'DREB%': [i[6] for i in team_stats],
        'STL': [i[7] for i in team_stats],
        'BLK': [i[8] for i in team_stats],
        'OPP_PTS_off_TOV': [i[9] for i in team_stats],
        'OPP_PTS_2nd_CHANCE': [i[10] for i in team_stats],
        'OPP_PTS_FB': [i[11] for i in team_stats],
        'OPP_PTS_PAINT': [i[12] for i in team_stats]})

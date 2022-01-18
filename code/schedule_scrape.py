## Objective: Scraping Basketball-Reference to get historical schedule data
##            & save the number of teams playing each day to validate
## Author: Teddy Einsidler
## Last Updated: November 15, 2021

### NOTE: GAMES MAY GET MOVED AND RESCHEDULED, SO THIS COULD NEED REGULAR
###       PERFORMANCE

### NOTE (11/15/2021): SUNDAYS ARE SPLIT BETWEEN EARLY AND LATE

### Early is before 6:00 pm ET

# Necessry Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import datetime

import re


def schedule_to_df(end_yr):
    """
    Given the ending year of the current (or a previous) season,
    will return a pandas DataFrame of a cleaned and fully-concatenated
    NBA schedule courtesy of data from https://www.basketball-reference.com
    """
    # To show who we are
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

    months = ['January', 'February',
              'March', 'April',
              'May', 'June',
              'July', 'August',
              'September', 'October',
              'November', 'December']

    # Initialize an empty list for the hrefs of the month-specific pages
    month_hrefs = []

    # Initialize the URL all of this originates from
    url_base = "https://www.basketball-reference.com"

    # Initialize the URL that will be parsed depending on the year provided
    url_parse = url_base+f"/leagues/NBA_{end_yr}_games.html"

    # GET the html
    req = requests.get(url_parse, headers)
    # Parse the html
    soup = BeautifulSoup(req.content, 'html.parser')

    # Iterate through the a tags within the website
    for link in soup.find_all('a'):
        # Conditionally select for links with a month as the text
        if link.get_text() in months:
            # Add each desired href to the list
            month_hrefs.append(link.get('href')+"#schedule")

    # Make a pandas DataFrame for the zeroth reset_index
    df1 = pd.DataFrame(pd.read_html((url_base+month_hrefs[0]))[0],)

    # Iterate through the remaining months listed
    for month_link in range(1,len(month_hrefs)):

        df2 = pd.DataFrame(pd.read_html((url_base+month_hrefs[month_link]))[0],)
        df1 = pd.concat(objs = [df1, df2], ignore_index = True)

    if "Playoffs" in df1["Date"].unique():
        playoffs_index = int(df1[df1["Date"] == "Playoffs"].index[0])
        df1["is_playoffs"] = df1.apply(lambda x: 1 if int(x.name) > playoffs_index
                                       else 0, axis = 1)
        df1.drop(index = playoffs_index, inplace = True)

    df1["Date"] = pd.to_datetime(df1["Date"], format = "%a, %b %d, %Y")

    df1.sort_values(by = "Date", ignore_index = True, inplace = True)

    col_rename = {
        "Date" : "date",
        "Start (ET)" : "start_et",
        "Visitor/Neutral" : "team_away",
        "PTS" : "pts_away",
        "Home/Neutral" : "team_home",
        "PTS.1" : "pts_home",
        "Unnamed: 6" : "box_score",
        "Unnamed: 7" : "overtime",
        "Attend." : "n_attending",
        "Notes" : "notes"
    }

    df1.rename(columns = col_rename, inplace = True)
    del df1["box_score"]

    return df1

def n_teams_per_day(end_yr):
    """
    Utilizing a pandas DataFrame created via the schedule_to_df function,
    returns a pandas DataFrame of the number of teams playing on each day of
    the season
    """

    # n_teams_df = schedule_to_df(end_yr).groupby("date").agg({"team_away" : lambda x: x.count()*2, "start_et" : lambda x: x.count()*2}).reset_index()
    n_teams_df = schedule_to_df(end_yr).groupby("date").agg({"team_away" : lambda x: x.count()*2}).reset_index()

    n_teams_df = schedule_to_df(end_yr)

    n_teams_df["is_early"] = n_teams_df.start_et.apply(lambda x: 0 if (str(x) == "nan")
                                                       or (int(re.match("^\d+", x)[0]) != 12
                                                           and (int(re.match("^\d+", x)[0]) > 6
                                                                and x[-1] == "p"))
                                                       or (x == "6:30p")
                                                       else 1)


    n_teams_df = n_teams_df.groupby("date").agg({"team_away" : lambda x: x.count()*2, "is_early" : lambda x: x.sum()*2}).rename(columns = {"team_away" : "n_teams", "is_early" : "n_teams_early"}).sort_values(by = "date").reset_index()

    n_teams_df["n_teams_night"] = n_teams_df["n_teams"] - n_teams_df["n_teams_early"]

    n_teams_df.index.names = ["season_day"]
    n_teams_df.index +=1

    n_teams_df.reset_index(inplace = True)

    return n_teams_df


def schedule_check_export(end_yr, mainpath = "data/nba_schedule"):
    """
    Given the end year of the current/a previous NBA season, it
    exports/overwrites the full schedule and checks if there is a pre-existing
    n_teams_per_day function .csv in an "n_teams" folder from the mainpath.
    If one exists, it checks if the schedule has changed and overwrites the
    existing .csv with the new information and stores the changes in a txt file.
    If one does not exist, it writes the file in the specified naming format
    and to the specified filepath.
    """

    ### HAVE A TEXT FILE TO WRITE OUT DATES WHEN THE SCHEDULE CHANGES
    ### AUTOMATICALLY RE-WRITE THE SCHEDULE CSV?

    ## Export the full schedule into a .csv
    # Initialize a string for the file path of the full schedule
    schedule_path = f"{mainpath}/full"
    # Initialize a string for the file name of the full schedule
    schedule_file = f"schedule_{(end_yr-1)}_{end_yr}.csv"
    # Running and exporting the full schedule
    schedule_to_df(end_yr).to_csv(f"{schedule_path}/{schedule_file}", index = False)

    # Initialize a string for the directory
    teams_path = f"{mainpath}/n_teams"
    # Initialize a string for the target file name
    target_file = f"n_teams_{(end_yr-1)}_{end_yr}.csv"

    # Get list of files in the directory
    teams_files = os.listdir(teams_path)
    # Get the n_teams DataFrame
    teams_new = n_teams_per_day(end_yr)

    # Check if the target has already been made
    if target_file in teams_files:
        teams_old = pd.read_csv(f"{teams_path}/{target_file}")
        ## Find if rows are different
        # Outer join via a merge to get the indicators
        merged = teams_new.merge(teams_old,
                                on = ["season_day", "n_teams"],
                                how = 'outer',
                                indicator=True).rename(columns = {"_merge" : "which_df"})

        indicator_dict = {
                            "left_only" : "New",
                            "right_only" : "Old"
        }

        merged['which_df'] = merged['which_df'].map(indicator_dict)
        merged.dropna(subset = ['which_df'], inplace = True)

        diff_records = merged.to_records(index = False)

        if len(diff_records) > 0:

            with open(f'reschedule_{(end_yr-1)}-{end_yr}.txt', 'a') as f:
                today = str(datetime.date.today().strftime("%m/%d/%Y"))
                f.writelines(f"---------- Log: {today} ----------")
                for diff in diff_records:
                    f.writelines(f'{diff}\n')

            # Overwrite with the updated n teams schedule data
            teams_new.to_csv(f"{teams_path}/{target_file}", index = False)

    else:
        teams_new.to_csv(f"{teams_path}/{target_file}", index = False)

# schedule_check_export(2022)

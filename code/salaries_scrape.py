## DraftKings Scraper
# Last Updated: 17 November 2021

### FUTURE: DON'T HARD CODE THE DATES INTO THIS FOR THE SEASON

### EITHER ADD CHECK WITHIN FUNCTION FOR THE TIME CALLED OR IN A
#### LARGER FUNCTION THAT CALLS THIS


## NEED TO THINK OF WHEN N_TEAMS == 4
# EACH GAME COULD SHOW UP AS INDIVIDUAL IDS BEFORE THE ENTIRE SLATE
# OR, THEY ARE SUPPOSED TO BE SPLIT BUT WE DON'T KNOW
# COULD CREATE LINEUPS FOR BOTH SCENARIOS TO BE SAFE AND INCORPORATE THAT
# INTO THE ALGORITHMIC PROCESS

# Days with no games
# November 25th
# December 24th
# February 18th - 23rd
# April 4th
# ————————————
# Playoffs start April 9th
import os
import pandas as pd
import re
import datetime
import requests


def get_last_id(path):
    """
    Returns the latest DraftKings ID from a folder of DraftKings csv files.
    """

    files = os.listdir(path)

    # Iterate through the file directory list and remove non-salary files
    for file in files:
        if not re.search("dk_\d+\.(csv|json)", file):
            files.remove(file)

    # Strip the file down to the ID integer
    files = [int(re.sub("dk_|\.(csv|json)", "", f)) for f in files]
    files.sort(reverse = True)

    return files[0]


def dk_csv(today = True, dk_path = "data/dk_salaries/dk_csv/2021_2022"):
    """
    Iterates through the DraftKings .csv files for either today (today = True)
    or the next day (today = False) and finds the files and IDs of interest.
    """

    # # Conditionally initialize the date based on the time
    # today = int(datetime.datetime.now().strftime("%H")) < 12

    game_day = datetime.date.today() if today else (datetime.date.today() + datetime.timedelta(days = 1))


    last_id = get_last_id(dk_path)

    n_teams_df = pd.read_csv("data/nba_schedule/n_teams/n_teams_2021_2022.csv",
                            parse_dates = ["date"])

    n_teams =  int(n_teams_df[n_teams_df["date"] == game_day.strftime("%Y-%m-%d")]["n_teams"])
    n_teams_night =  int(n_teams_df[n_teams_df["date"] == game_day.strftime("%Y-%m-%d")]["n_teams_night"])


    # Initialize a dictionary to append potential IDs and their teams
    dk_dict = {
        "ids" : [],
        "teams" : []
    }

    while True:

        try:

            print(f"{last_id}\n")

            df = pd.read_csv(f"https://www.draftkings.com/lineup/getavailableplayerscsv?contestTypeId=70&draftGroupId={last_id}")
            playing_teams = list(df["TeamAbbrev"].unique())

            if ("PG" in df["Position"].unique()
                and "T1" not in list(df["Roster Position"].unique())
                and re.search("BENCH", df["Roster Position"][0]) == None
                and game_day.strftime("%m/%d/%Y") in df["Game Info"].iloc[0]):

                if len(list(df["TeamAbbrev"].unique())) == n_teams:

                    df.to_csv(f"{dk_path}/dk_{last_id}.csv")

                    return

                else:

                    dk_dict['ids'].append(last_id)
                    dk_dict['teams'].append(list(df["TeamAbbrev"].unique()))

                    last_id += 1

                    if len(dk_dict['ids']) > 1:

                        for i in range((len(dk_dict['ids'])-1)):
                            for j in range((i+1),(len(dk_dict['ids']))):

                                if (len(set(dk_dict['teams'][i]).intersection(set(dk_dict['teams'][j]))) == 0
                                    and (len(dk_dict['teams'][i]) + len(dk_dict['teams'][j])) == n_teams):

                                    df_i = pd.read_csv(f"https://www.draftkings.com/lineup/getavailableplayerscsv?contestTypeId=70&draftGroupId={dk_dict['ids'][i]}")
                                    df_j = pd.read_csv(f"https://www.draftkings.com/lineup/getavailableplayerscsv?contestTypeId=70&draftGroupId={dk_dict['ids'][j]}")

                                    df_i.to_csv(f"{dk_path}/dk_{dk_dict['ids'][i]}.csv")
                                    df_j.to_csv(f"{dk_path}/dk_{dk_dict['ids'][j]}.csv")

                                    return

                                else:
                                    continue
                    else:
                        continue

            else:
                last_id +=1
                continue

        except:
            last_id += 1
            continue

        else:
            last_id += 1
            continue




### NEED TO TAKE CARE OF ISSUE IF SPLIT INTO DAY AND NIGHT
# Because dates are strange in the JSON files, dowloading
# The desired data will require the list from the csv files
def dk_json(json_path = "data/dk_salaries/dk_json/2021_2022",
            csv_path = "data/dk_salaries/dk_csv/2021_2022"):
    """
    Relying on the calling of dk_csv, retrieves the JSON file
    of the last DraftKings ID from the csv foldler.
    """

    last_id = get_last_id(csv_path)

    url = f"https://api.draftkings.com/draftgroups/v1/draftgroups/{last_id}/draftables?format=json"

    req = requests.get(url)

    with open(f"{json_path}/dk_{last_id}.json", 'w') as f:
        f.write(req.text)

dk_csv()
dk_json()

import pandas as pd
import json
from salaries_scrape import get_last_id

# def playing_tonight():    
#     url = 'https://www.sportsline.com/nba/expert-projections/simulation/'
#
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     table = soup.find_all("table")[0]
#
#     data = [[cell.text for cell in row.find_all(["th","td"])]
#                             for row in table.find_all("tr")]
#     #print(data)
#     df = pd.DataFrame(data)
#
#     df.columns = df.iloc[0,:]
#     df.drop(index=0,inplace=True)
#     return df[['PLAYER  ','POS  ']]


def playing_tonight(questionable = True,
                    json_path = "data/dk_salaries/dk_json/2021_2022"):
    """
    Utilizing the DraftKings JSON file to subset who is playing tonight.
    """

    id_tonight = get_last_id(json_path)

    with open(f'{json_path}/dk_{id_tonight}.json') as f:
        data = json.load(f)

    df = pd.DataFrame.from_records(data["draftables"])

    if questionable:
        df = df[df["status"] != 'OUT'].reset_index()
    else:
        df = df[df["status"] == 'None'].reset_index()

    return df[["playerId", "displayName", "teamAbbreviation", "position", "rosterSlotId", "salary", "status"]]

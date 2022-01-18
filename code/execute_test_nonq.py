from projections import projection_model
import cleaning
from playing_tonight import playing_tonight
import pandas as pd
import itertools
import pulp
import numpy as np

import datetime
import re

import warnings
warnings.filterwarnings("ignore")

### ISSUES WITH CHROMIUM
from statistics_scrape import nba_season_stats

game_day = datetime.date.today().strftime("%b-%d-%Y")

##### VAR Modeling
# data = cleaning.logs_and_defense()
data = pd.read_csv("data/g_logs_defense.csv")

tonight_df = playing_tonight(questionable = False, json_path = "data/dk_salaries/dk_json/2021_2022")

players_tonight = list(tonight_df.displayName.unique())

projections = projection_model(players_tonight)

projections = pd.merge(tonight_df,
                       projections,
                       left_on = ['displayName', 'teamAbbreviation'],
                       right_on= ['Player', 'Team'],
                       how='inner').drop(columns = ['Player', 'Team'])


projections['costPerPoint'] = round(projections['salary']/projections['DK_proj'],2)

projections.sort_values(by='costPerPoint', ascending=True,inplace=True)

projections['pointsRank'] = projections['DK_proj'].rank(ascending=False)

projections['salaryRank'] = projections['salary'].rank(ascending=False)

projections['eligible'] = np.where(np.abs((projections['pointsRank']) - (projections['salaryRank']))<= 30,True,False)

projections.to_csv(f'data/projections/2021_2022/projections_full_{game_day}.csv',index=False)

## WHY after filter?

projections = projections[projections['eligible'] == True]

projections.to_csv(f'data/projections/2021_2022/projections_1-20_{game_day}.csv',index=False)

projection_columns = ['playerId',
                      'displayName',
                      'teamAbbreviation',
                      'position',
                      'rosterSlotId',
                      'salary',
                      'status',
                      'DK_proj',
                      'pointsRank',
                      'salaryRank',
                      'eligible',
                      'costPerPoint']

projections = projections[projection_columns].rename(columns = {"DK_proj" : "points"})

roster_ids = list(projections.rosterSlotId.unique())
roster_ids.sort()

# Set index as unique identifiers
projections.set_index(keys = ['playerId', 'displayName', 'teamAbbreviation',
                                'position', 'rosterSlotId'],
                      inplace = True)

legal_assignments = projections.index   # tuples of (name, pos)
id_set = projections.index.unique(0)  # a conveniece

costs = projections['salary'].to_dict()
values = projections['points'].to_dict()

salary_cap = 50000

output_list = []


# set up LP
draft = pulp.LpVariable.dicts('selected', legal_assignments, cat='Binary')

prob = pulp.LpProblem('the draft', pulp.LpMaximize)

# obj
prob += pulp.lpSum([draft[l, m, n, o, p]*values[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments])

# salary cap
prob += pulp.lpSum([draft[l, m, n, o, p]*costs[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments]) <= salary_cap

# pick 1 position
prob += pulp.lpSum([(draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[0])]) == 1

# pick 1 position
prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[1]]) == 1

# pick 1 position
prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[2]]) == 1

# pick 1 position
prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[3]]) == 1

# pick 1 position
prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[4]]) == 1

# pick 1 position
prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[5]]) == 1

# pick 1 position
prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[6]]) == 1

# pick 1 position
prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if p == roster_ids[7]]) == 1

# use each player at most only once
for id in id_set:
    prob += pulp.lpSum([draft[l, m, n, o, p] for (l, m, n, o, p) in legal_assignments if l == id]) <=1

prob.solve()

for idx in draft:
    if draft[idx].varValue:
        rostered_df = projections[projections.index == idx]
        output_list.append([idx[0], idx[1], idx[2], idx[3], idx[4], int(rostered_df['salary']), float(rostered_df['points'])])

## Add the lineup totals
tot_salary = 0
tot_points = 0
for player in output_list:
    tot_salary += player[5]
    tot_points += player[6]

output_list.append(['total', 'total', 'total', 'total', 'total', tot_salary, tot_points])

output_df = pd.DataFrame(output_list, columns = ['playerId', 'displayName', 'teamAbbreviation',
                                          'position', 'rosterSlotId', 'salary', 'points'])

# Utilizing the SORTED list of roster_ids
# In case the numbering changes, the order will likely stay the same
rosterSlotId_dict = {
    roster_ids[0] : "PG",
    roster_ids[1] : "SG",
    roster_ids[2] : "PF",
    roster_ids[3] : "SF",
    roster_ids[4] : "C",
    roster_ids[5] : "F",
    roster_ids[6] : "G",
    roster_ids[7] : "UTIL",
    "total" : "total"
}

# Make a column to convert rosterSlotId to the common name
id_to_name = output_df['rosterSlotId'].map(rosterSlotId_dict)
output_df.insert(5, 'rosterSlotName', id_to_name)

output_df.to_csv(f"data/projections/2021_2022/no_question_projections_{game_day}.csv", index = False)

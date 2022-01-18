from statistics_scrape import nba_season_stats, nba_defense
from special_stats import double_double, triple_double
import pandas as pd

def clean_game_log(season = "2021-22",
                path = "data/game_logs",
                past_file = "2016-21_game_logs.csv"):
    """
    Combine the previous seasons with the current season in the game logs.
    """

    # Read in the current season
    current = nba_season_stats()

    # Read in the previous seasons
    previous = pd.read_csv(f'{path}/{past_file}',
                            parse_dates = ["Date"])


    #### Feature Engineering
    # Date column to datetime
    current['Date'] = pd.to_datetime(current['Date'])

    # Create Season column
    current['Season'] = season

    # Concat to single dataframe
    frames = [previous, current]
    game_logs_all = pd.concat(frames)
    game_logs_all.sort_index(inplace=True)

    # Drop columns with percentages

    game_logs_all.drop(columns=['FT%', '3P%', 'FG%'], inplace=True)

    # Save numerical columns as ints

    game_logs_all[['Min', 'Pts', 'FGM','FGA','3PM', '3PA', 'FTM', 'FTA', 'OREB',
           'DREB','REB','AST','STL','BLK','TOV','PF', '+/-']] = game_logs_all[['Min', 'Pts', 'FGM','FGA','3PM', '3PA', 'FTM', 'FTA', 'OREB',
           'DREB','REB','AST','STL','BLK','TOV','PF', '+/-']].astype(str).astype(int)

    # Create Double double column
    game_logs_all['dubdub'] = game_logs_all.apply(double_double, axis=1)

    # Create Triple double column
    game_logs_all['tripdub'] = game_logs_all.apply(triple_double, axis=1)

    # Create Draft kings score column (based on draftkings formula)
    game_logs_all['DraftKings'] = game_logs_all['Pts'] + .5*game_logs_all['3PM'] + 1.25*game_logs_all['REB'] + 1.5*game_logs_all['AST'] \
    + 2*game_logs_all['STL'] + 2*game_logs_all['BLK'] -.5*game_logs_all['TOV'] + 1.5*game_logs_all['dubdub'] + 3*game_logs_all['tripdub']

    # Home or away column: 1 for away, 0 for home
    game_logs_all['Home/Away'] = game_logs_all['Match-up'].str.contains('@').astype(int)

    # Full names for 'Match-up'
    game_logs_all['Match-up'] = game_logs_all['Match-up'].map({'vs.UTA': 'Utah Jazz', '@POR':'Portland Trailblazers',
                            '@GSW':'Golden State Warriors', 'vs.SAS':'San Antonio Spurs',
                            '@IND':'Indiana Pacers','vs.DAL':'Dallas Mavericks','vs.CHA':'Charlotte Hornets',
                            'vs.DET':'Detroit Pistons','@TOR':'Toronto Raptors','@MIL': 'Milwaukee Bucks',
                            '@MEM': 'Memphis Grizzlies','vs.MIN':'Minnesota Timberwolves','vs.DEN': 'Denver Nuggets',
                            '@NOP': 'New Orleans Pelicans','vs.MIA': 'Miami Heat','@LAL':'Los Angeles Lakers',
                            'vs.HOU':'Houston Rockets','@ORL':'Orlando Magic','@PHX':'Phoenix Suns','vs.SAC':'Sacramento Kings',
                            'vs.OKC':'Oklahoma City Thunder','@PHI':'Philadelphia 76ers','@BOS':'Boston Celtics',
                            'vs.BKN':'Brooklyn Nets','vs.WAS':'Washington Wizards','@ATL':'Atlanta Hawks',
                            '@SAC':'Sacramento Kings','vs.BOS':'Boston Celtics','@CHI':'Chicago Bulls',
                            'vs.LAC': 'LA Clippers','vs.CLE':'Cleveland Cavaliers','@DAL':'Dallas Mavericks',
                            'vs.PHX': 'Phoenix Suns','vs.GSW':'Golden State Warriors','@OKC':'Oklahoma City Thunder',
                            '@UTA':'Utah Jazz','vs.LAL':'Los Angeles Lakers','@MIA':'Miami Heat','vs.IND':'Indiana Pacers',
                            '@BKN':'Brooklyn Nets','vs.ORL':'Orlando Magic','@DET':'Detroit Pistons','vs.MEM':'Memphis Grizzlies',
                            '@CLE':'Cleveland Cavaliers','@CHA':'Charlotte Hornets','@DEN':'Denver Nuggets','vs.POR':'Portland Trailblazers',
                            'vs.NOP':'New Orleans Pelicans','@SAS':'San Antonio Spurs','vs.ATL':'Atlanta Hawks','@NYK':'New York Knicks',
                            'vs.MIL':'Milwaukee Bucks','@LAC':'LA Clippers','@HOU':'Houston Rockets','vs.CHI':'Chicago Bulls',
                            'vs.NYK':'New York Knicks','@MIN':'Minnesota Timberwolves','vs.PHI':'Philadelphia 76ers','@WAS':'Washington Wizards',
                            'vs.TOR':'Toronto Raptors'})

    # Save as csv
    # game_logs_all.to_csv('data/game_logs_all.csv')
    game_logs_all.to_csv(f'{path}/to_current_game_logs.csv',
                        index = False)

    return game_logs_all


def clean_defense(season = "2021-22",
                    path = "data/defense",
                    past_file = "2016-21_defense.csv"):
    """
    """

    previous_d = pd.read_csv(f'{path}/{past_file}')

    current_d = nba_defense(season)


    ## Concatenate defenses
    defenses = [previous_d ,current_d]


    defenses = pd.concat(defenses)

    defenses['Team'].replace('Portland Trail Blazers','Portland Trailblazers', inplace=True)

    defenses.to_csv(f'{path}/to_current_defense.csv',
                        index = False)

    return defenses

def logs_and_defense(season = "2021-22",
                    g_path = "data/game_logs",
                    g_past_file = "2016-21_game_logs.csv",
                    d_path = "data/defense",
                    d_past_file = "2016-21_defense.csv"):
    """
    """

    # Merge game logs and defenses
    total = pd.merge(clean_game_log(season, g_path, g_past_file),
                        clean_defense(season, d_path, d_past_file),
                        left_on=['Match-up','Season'],
                        right_on=['Team','Season'],
                        how='inner')


    ### More feature Engineering
    # Drop columns that are not relevant
    total = total[['Date', 'Player', 'Team_x', 'Match-up', 'W/L', 'Min', 'Pts', 'FGM',
           'FGA', '3PM', '3PA', 'FTM', 'FTA', 'OREB', 'DREB_x', 'REB', 'AST',
           'STL_x', 'BLK_x', 'TOV', 'PF', '+/-', 'Season', 'dubdub', 'tripdub',
           'DraftKings', 'Home/Away', 'DEF_RTG','DREB%', 'STL_y', 'BLK_y', 'OPP_PTS_off_TOV',
           'OPP_PTS_2nd_CHANCE', 'OPP_PTS_FB', 'OPP_PTS_PAINT']]

    # Rename columns to more appealing titles
    total.rename(columns={'DEF_RTG':'OPP_DEF_RTG',
              'DREB%':'OPP_DREB%',
              'STL_y':'OPP_STL',
              'BLK_y':'OPP_BLK',
                         'DREB_x':'DREB',
                         'STL_x':'STL',
                         'BLK_x':'BLK',
                         'Team_x':'Team',
                         'DraftKings':'DK_SCORE',
                         'dubdub':'Dub/Dub',
                         'tripdub':'Trip/Dub'}, inplace=True)

    # Binarize 'W/L' column
    total['W/L'] = total['W/L'].map({'W': 1, 'L': 0})

    # Reorder columns
    total = total[['Date','Season', 'Player', 'Team', 'Match-up','Home/Away', 'W/L', 'Min', 'Pts', 'FGM', 'FGA',
           '3PM', '3PA', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK',
           'TOV', 'PF', '+/-', 'Dub/Dub', 'Trip/Dub', 'OPP_DEF_RTG', 'OPP_DREB%', 'OPP_STL', 'OPP_BLK',
           'OPP_PTS_off_TOV', 'OPP_PTS_2nd_CHANCE', 'OPP_PTS_FB', 'OPP_PTS_PAINT','DK_SCORE']]

    # Save to csv for modeling
    total.to_csv('data/g_logs_defense.csv',index=False)

    return total


clean_game_log()
clean_defense()
logs_and_defense()

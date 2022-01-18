#### MODEL TO RUN FOR ALL OF TONIGHT'S PLAYERS
### NEED TO CHANGE SUCH THAT IT IS NOT HARD-CODED

from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd

def projection_model(player_list):

    #### NEED TO FIX HARD CODING OF projection_model
    twenty_one = pd.read_csv("data/game_logs/to_current_game_logs.csv", parse_dates = ['Date'])
    twenty_one = twenty_one[twenty_one['Season'] == '2021-22'].reset_index()
    data = pd.read_csv("data/g_logs_defense.csv")

    empty_list = []
    for player in player_list:
        if ((twenty_one[twenty_one['Player']== player]['Min'].mean()) >= 10)&((data[data['Player'] == player]['Date'].count()) > 10)&\
        (twenty_one[twenty_one['Player'] == player]['Date'].count()> 2):
            df = data[data['Player'] == player]
            df.index = pd.DatetimeIndex(df['Date'])
            df.drop(columns='Date',inplace=True)
            df.sort_index(inplace=True)

            player = df['Player'][0]

            team = df['Team'][0]

            last_game = df[['DK_SCORE', 'Pts','AST','REB']].iloc[[-1]]

            last_dk = 0
            last_points = 0
            last_reb = 0
            last_ast = 0


            # Confirm Stationarity of the data
            def interpret_dftest(dftest):
                dfoutput = pd.Series(dftest[0:3], index=['Test Statistic','p-value', 'Lag Used'])
                return dfoutput


            # Check if draftkings is stationary
            dk_test = interpret_dftest(adfuller(df['DK_SCORE']))

            if dk_test[1] > .05:
                df['DK_SCORE'] = df['DK_SCORE'].diff(1)
                last_dk = int(last_game['DK_SCORE'])


            # Check if points is stationary
            pts_test = interpret_dftest(adfuller(df['Pts']))

            if pts_test[1] > .05:
                df['Pts'] = df['Pts'].diff(1)
                last_points = int(last_game['Pts'])


            # Check if rebounds is stationary
            reb_test = interpret_dftest(adfuller(df['REB']))

            if reb_test[1] > .05:
                df['REB'] = df['REB'].diff(1)
                last_reb = int(last_game['REB'])


            # Check if assists is stationary
            ast_test = interpret_dftest(adfuller(df['AST']))

            if ast_test[1] > .05:
                df['AST'] = df['AST'].diff(1)
                last_ast = int(last_game['AST'])


            df = df[['DK_SCORE','Pts','REB','AST']]

            df.dropna(inplace=True)

            train, test = train_test_split(df,shuffle=False, test_size = .3)

            model = VAR(train)

            ts_model = model.fit(maxlags=3)

            forecast = ts_model.forecast(train.values, len(test))

            next_game = ts_model.forecast(train.values, 1)

            empty_list.append([player, team, last_dk + round(next_game[0][0],2),last_points + round(next_game[0][1],2),
                             last_reb + round(next_game[0][2],2),last_ast + round(next_game[0][3],2),
                              round(mean_squared_error(test.values[:, 0], forecast[:, 0]), 2),
                              round(mean_squared_error(test.values[:, 1], forecast[:, 1]), 2),
                              round(mean_squared_error(test.values[:, 2], forecast[:, 2]), 2),
                              round(mean_squared_error(test.values[:, 3], forecast[:, 3]), 2)])


    return pd.DataFrame(empty_list, columns=['Player', 'Team','DK_proj','Pts_proj','Reb_proj','Ast_proj','MSE_DK',
                                            'MSE_Pts','MSE_Reb','MSE_Ast'])

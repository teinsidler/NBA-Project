


### 3 days, 50 threshold


def computeRSI (data, time_window):
    diff = data.diff(1).dropna()        # diff in one field(one day)

    #this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff

    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]

    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]

    # check pandas documentation for ewm
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    # values are related to exponential decay
    # we set com=time_window-1 so we get decay alpha=1/time_window
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()

    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    return rsi





    def nba_eval_RSI(GID, num_games, threshold = 50, fanduel = True, dataframe = df):
        '''
        Returns a nested dictionary, containing a confusion matrix
        and other basic statistics for an NBA player based on the RSI.

        The 'GID' numeric value from the rotoguru data must be used and the 'num_games' represents
        one less than the number of games involved in the RSI and moving average calculations.

        The default 'threshold' for the RSI boundary to buy is set to 50.

        There is the choice between platform on interest: FanDuel (fanduel = True).
        fanduel = False is for DraftKings. The default platform is FanDuel.

        The 'dataframe' that is instantiated from rotoguru is to be referenced here.
        It is defaulted to df

        This utilizes computeRSI(data, time_window).

        Pandas and numpy (as np) must be imported
        '''

        # Subset based on GID
        player_df = df[df['GID'] == GID]

        # Get the player's name
        player_name = list(player_df["First  Last"].unique())[0]

        # Conditionally add FanDuel or DraftKings points and salary
        if fanduel:
            dfs_points = 'FDP'
            dfs_sal = 'FD Sal'
        else:
            dfs_points = 'DKP'
            dfs_sal = 'DK Sal'

        # Subset the player dataframe to more relevant columns
        player_df = player_df[["First  Last", "Date", "Team pts", "Minutes", dfs_points, dfs_sal]]

     # Reset the indices of this subset
     player_df.reset_index(drop=True)

     # Sort by earliest date
     player_df = player_df.sort_values('Date', ascending = True)

     # Drop games where the player did not play for one minute
     player_df = player_df.drop(player_df[player_df.Minutes < 1].index)

     # Create a column to evaluate a player's price per fantasy point (salary/points)
     player_df["Salary/Point"] = player_df[dfs_sal] / player_df[dfs_points]

     # Create a column of the moving average
     player_df['Salary/Point_SMA'] = player_df["Salary/Point"].rolling(window=(num_games)).mean()

     # Create a column that calcuates the RSI values for the number of games
     player_df['RSI'] = computeRSI(player_df["Salary/Point"], (num_games-1))

     # Calculate the daily percent change in the players' fantasy points
     player_df["Percent_Change"] = player_df[dfs_points].pct_change() * 100

     # Create a binary column that indicates whether a buy signal (1) occurs
     # A.k.a the RSI passes the threshold
     # This will signal to buy the player for the following game in which they play in the dataset
     player_df['Signal'] = np.where(player_df['RSI'] >= threshold, 1, 0)

     # Create a 'Bought' column that utilizes the 'Signal' column and shifts it down
     # to demonstrate the day that the RSI indicates to buy the player
     player_df['Bought'] = player_df.Signal.shift(1)

     # Fill the NaN that is introduced into the 'Bought' column by the shift
     player_df['Bought'] = player_df['Bought'].fillna(0)

     # Creating a 'PosChange' column as a binary indicator as to whether
     # the player had a positive increase in fantasy points from the previous game



     ############## RECENT CHANGE
  #     player_df['PosChange'] = np.where(player_df['Percent_Change'] > 0, 1, 0)


  def nba_eval_RSI(GID, num_games, threshold = 50, fanduel = True, dataframe = df):
    '''
    Returns a nested dictionary, containing a confusion matrix
    and other basic statistics for an NBA player based on the RSI.

    The 'GID' numeric value from the rotoguru data must be used and the 'num_games' represents
    one less than the number of games involved in the RSI and moving average calculations.

    The default 'threshold' for the RSI boundary to buy is set to 50.

    There is the choice between platform on interest: FanDuel (fanduel = True).
    fanduel = False is for DraftKings. The default platform is FanDuel.

    The 'dataframe' that is instantiated from rotoguru is to be referenced here.
    It is defaulted to df

    This utilizes computeRSI(data, time_window).

    Pandas and numpy (as np) must be imported
    '''

    # Subset based on GID
    player_df = df[df['GID'] == GID]

    # Get the player's name
    player_name = list(player_df["First  Last"].unique())[0]

    # Conditionally add FanDuel or DraftKings points and salary
    if fanduel:
        dfs_points = 'FDP'
        dfs_sal = 'FD Sal'
    else:
        dfs_points = 'DKP'
        dfs_sal = 'DK Sal'

    # Subset the player dataframe to more relevant columns
    player_df = player_df[["First  Last", "Date", "Team pts", "Minutes", dfs_points, dfs_sal]]

    # Reset the indices of this subset
    player_df.reset_index(drop=True)

    # Sort by earliest date
    player_df = player_df.sort_values('Date', ascending = True)

    # Drop games where the player did not play for one minute
    player_df = player_df.drop(player_df[player_df.Minutes < 1].index)

    # Create a column to evaluate a player's price per fantasy point (salary/points)
    player_df["Salary/Point"] = player_df[dfs_sal] / player_df[dfs_points]

    # Create a column of the moving average
    player_df['Salary/Point_SMA'] = player_df["Salary/Point"].rolling(window=(num_games)).mean()

    # Create a column that calcuates the RSI values for the number of games
    player_df['RSI'] = computeRSI(player_df["Salary/Point"], (num_games-1))

    # Calculate the daily percent change in the players' fantasy points
    player_df["Percent_Change"] = player_df[dfs_points].pct_change() * 100

    # Create a binary column that indicates whether a buy signal (1) occurs
    # A.k.a the RSI passes the threshold
    # This will signal to buy the player for the following game in which they play in the dataset
    player_df['Signal'] = np.where(player_df['RSI'] >= threshold, 1, 0)

    # Create a 'Bought' column that utilizes the 'Signal' column and shifts it down
    # to demonstrate the day that the RSI indicates to buy the player
    player_df['Bought'] = player_df.Signal.shift(1)

    # Fill the NaN that is introduced into the 'Bought' column by the shift
    player_df['Bought'] = player_df['Bought'].fillna(0)

    # Creating a 'PosChange' column as a binary indicator as to whether
    # the player had a positive increase in fantasy points from the previous game



    ############## RECENT CHANGE
#     player_df['PosChange'] = np.where(player_df['Percent_Change'] > 0, 1, 0)



    # Issue: just being positive is not enough, varied thresholds for the players
    # Make threshold over median points or median salary/points
    # Above the moving average?
    player_df['PosChange'] = np.where(player_df[dfs_points] > player_df[dfs_points].median(), 1, 0)


    # Create a confusion maxtrix to determine the accuracy of the RSI
    confusion_matrix = pd.crosstab(player_df['PosChange'], player_df['Bought'],
                                   rownames=['Actual'], colnames=['Predicted'])

    # Calculate accuracy
    accuracy = np.diag(confusion_matrix).sum() / confusion_matrix.to_numpy().sum()

    # Find the frequency of singals for the player over the tested games
    freq_signal = player_df['Signal'].sum() / player_df['Signal'].count()

    # Find the mean fantasy points for when the player was bought
    # versus when the player was not bought
    bought_mean = player_df.loc[player_df['Bought'] == 1][dfs_points].mean()
    not_bought_mean = player_df.loc[player_df['Bought'] == 0][dfs_points].mean()

    # Find the standard deviation of fantasy points for when the player was bought
    # versus when the player was not bought
    bought_sd = player_df.loc[player_df['Bought'] == 1][dfs_points].std()
    not_bought_sd = player_df.loc[player_df['Bought'] == 0][dfs_points].std()

    # Create a dictionary of interesting statistics
    player_dict = {'name': player_name,
                   'number of games': num_games,
                   'threshold': threshold,
                   'confusion matrix': confusion_matrix,
                   'accuracy': accuracy,
                   'signal frequency': freq_signal,
                   'bought mean dfs': bought_mean,
                   'not mean dfs': not_bought_mean,
                   'bought st dev dfs': bought_sd,
                   'not st dev dfs': not_bought_sd}

    return player_dict

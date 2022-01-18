# Function if player has a double double

def double_double(row):
    val = 0
    if (row['Pts'] >= 10) & (row['AST'] >= 10) | \
    (row['Pts'] >=10) & (row['REB'] >= 10) | (row['AST'] >=10) & (row['REB'] >= 10):
        val += 1
    return val

# Function if player has a triple double

def triple_double(row):
    val = 0
    if (row['Pts'] >= 10) & (row['AST'] >= 10) & (row['REB'] >=10) | \
    (row['Pts'] >=10) & (row['AST'] >= 10) & (row['STL'] >= 10) | \
    (row['Pts'] >=10) & (row['REB'] >= 10) & (row['BLK'] >= 10) | \
    (row['Pts'] >=10) & (row['AST'] >= 10) & (row['BLK'] >= 10):
        val += 1
    return val

import pandas as pd

# Read the CSV file
df = pd.read_csv('sportsbook_odds.csv')

# Create a new dataframe with the desired structure
cleaned_df = pd.DataFrame()

# Add Sport column (all NFL in this case)
cleaned_df['Sport'] = 'NFL'

# Get unique matches
unique_matches = df[['Match Date', 'Home Team', 'Away Team']].drop_duplicates()

# Initialize lists to store the reorganized data
match_dates = []
home_teams = []
away_teams = []
home_odds = []
away_odds = []
bookmakers = []

def american_to_decimal(american_odds):
    # Remove 'ML' suffix and convert to integer
    american = int(american_odds.replace(' ML', ''))
    if american > 0:
        return round(american/100 + 1, 3)
    else:
        return round(100/abs(american) + 1, 3)

# Iterate through unique matches and bookmakers
for _, match in unique_matches.iterrows():
    match_data = df[
        (df['Match Date'] == match['Match Date']) & 
        (df['Home Team'] == match['Home Team']) &
        (df['Away Team'] == match['Away Team'])
    ]
    
    # Get unique bookmakers for this match
    for bookmaker in match_data['Bookmaker'].unique():
        match_odds = match_data[match_data['Bookmaker'] == bookmaker]
        
        # Only process if we have odds for both teams
        if len(match_odds) == 2:
            home_team_odds = american_to_decimal(match_odds[match_odds['Team'] == match['Home Team']]['Price'].iloc[0])
            away_team_odds = american_to_decimal(match_odds[match_odds['Team'] == match['Away Team']]['Price'].iloc[0])
            
            match_dates.append(match['Match Date'])
            home_teams.append(match['Home Team'])
            away_teams.append(match['Away Team'])
            home_odds.append(home_team_odds)
            away_odds.append(away_team_odds)
            bookmakers.append(bookmaker)

# Add columns to cleaned dataframe
cleaned_df['Match Date'] = match_dates
cleaned_df['Home Team'] = home_teams
cleaned_df['Away Team'] = away_teams
cleaned_df['Home Team Odds'] = home_odds
cleaned_df['Away Team Odds'] = away_odds
cleaned_df['Bookmaker'] = bookmakers

# Save to new CSV
cleaned_df.to_csv('cleaned_sportsbook_odds.csv', index=False)
print("Data has been cleaned and saved to cleaned_sportsbook_odds.csv")

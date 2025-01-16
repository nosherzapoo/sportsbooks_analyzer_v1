import pandas as pd
from datetime import datetime

def sync_results():
    # Read the CSV files
    today = datetime.now().strftime('%Y%m%d')
    results_df = pd.read_csv(f'game_results_{today}.csv')
    games_df = pd.read_csv(f'game_odds_{today}.csv')

    # Convert event time to datetime for comparison
    results_df['Event Time'] = pd.to_datetime(results_df['Event Time'])
    games_df['Match Date'] = pd.to_datetime(games_df['Match Date'], format='%b %d, %Y, %I:%M %p')

    # Merge the dataframes on team names and sport
    merged_df = pd.merge(results_df, games_df, 
                        left_on=['Sport', 'Home Team', 'Away Team'],
                        right_on=['Sport', 'Home Team', 'Away Team'],
                        how='left')

    # Add winner column for completed games
    def determine_winner(row):
        if row['Status'] != 'Completed':
            return 'Not Completed'
        if pd.isna(row['Home Score']) or pd.isna(row['Away Score']):
            return 'Unknown'
        if float(row['Home Score']) > float(row['Away Score']):
            return 'Home'
        elif float(row['Home Score']) < float(row['Away Score']):
            return 'Away'
        else:
            return 'Tie'

    merged_df['Match Result'] = merged_df.apply(determine_winner, axis=1)

    # Select and rename columns for output
    output_df = merged_df[[
        'Sport', 'Match Date', 'Home Team', 'Away Team',
        'Home Score', 'Away Score', 'Status', 'Game ID',
        'Home Team Odds', 'Away Team Odds', 'Bookmaker',
        'Match Result'
    ]]

    # Save to new CSV
    output_filename = f'synced_results_{datetime.now().strftime("%Y%m%d")}.csv'
    output_df.to_csv(output_filename, index=False)
    return output_filename

if __name__ == "__main__":
    sync_results()

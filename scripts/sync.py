import pandas as pd
from datetime import datetime
import os

def sync_data():
    try:
        # Get today's date
        today = '2025031'
        
        # Required files
        # Get yesterday's date for odds file
        odds_file = f'data/game_odds_{today}.csv'
        results_file = f'data/game_results_{today}.csv'
        
        # Check if files exist
        if not os.path.exists(odds_file) or not os.path.exists(results_file):
            print(f"Missing required files for sync: {odds_file} or {results_file}")
            return False
        
        # Read the files
        odds_df = pd.read_csv(odds_file)
        results_df = pd.read_csv(results_file)
        
        # Merge odds data with results on Sport, Home Team, Away Team
        merged_df = pd.merge(
            results_df,
            odds_df[['Sport', 'Match Date', 'Home Team', 'Away Team', 'Home Team Odds', 'Away Team Odds', 'Bookmaker', 'Compiled_At']],
            on=['Sport', 'Home Team', 'Away Team'],
            how='outer',
            suffixes=('', '_time')
        )
        
        # Drop rows without odds
        merged_df = merged_df.dropna(subset=['Home Team Odds', 'Away Team Odds'])
        
        # Calculate win percentages for each bookmaker
        bookmaker_stats = []
        for bookmaker in merged_df['Bookmaker'].unique():
            bookmaker_df = merged_df[merged_df['Bookmaker'] == bookmaker]
            
            # Determine favorites and underdogs based on odds
            bookmaker_df['Favorite'] = bookmaker_df.apply(
                lambda x: 'Home' if x['Home Team Odds'] < x['Away Team Odds'] else 'Away', axis=1
            )
            
            # Calculate actual winners
            bookmaker_df['Winner'] = bookmaker_df.apply(
                lambda x: 'Home' if x['Home Score'] > x['Away Score'] 
                else 'Away' if x['Away Score'] > x['Home Score']
                else 'Draw', axis=1
            )
            
            # Calculate win percentages and unknown games
            total_games = bookmaker_df.shape[0]
            completed_games = bookmaker_df[bookmaker_df['Status'] == 'Completed'].shape[0]
            unknown_games = bookmaker_df[bookmaker_df['Status'] == 'Unknown'].shape[0]
            
            if completed_games > 0:
                favorite_wins = bookmaker_df[
                    (bookmaker_df['Status'] == 'Completed') & 
                    (bookmaker_df['Favorite'] == bookmaker_df['Winner'])
                ].shape[0]
                underdog_wins = completed_games - favorite_wins
                
                bookmaker_stats.append({
                    'Bookmaker': bookmaker,
                    'Underdog Wins': underdog_wins,
                    'Underdog Win %': round(underdog_wins / completed_games * 100, 2),
                    'Favorite Wins': favorite_wins,
                    'Favorite Win %': round(favorite_wins / completed_games * 100, 2),
                    'Unknown Games': unknown_games
                })
        
        # Create stats DataFrame
        stats_df = pd.DataFrame(bookmaker_stats)
        
        # Save merged data with stats at the top
        output_file = f'data/sportsbook_performance_{today}.csv'
        with open(output_file, 'w') as f:
            stats_df.to_csv(f, index=False)
            f.write('\n')  # Add blank line between tables
            merged_df.to_csv(f, index=False)
            
        print(f"Synced results saved to {output_file}")
        return True
            
    except Exception as e:
        print(f"Error during sync: {e}")
        return False

if __name__ == "__main__":
    sync_data()

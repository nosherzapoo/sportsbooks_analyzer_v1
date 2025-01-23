import pandas as pd
from datetime import datetime
import os

def sync_data():
    try:
        # Get today's date
        today = datetime.now().strftime('%Y%m%d')
        
        # Required files
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
        
        # Save merged data
        output_file = f'data/sportsbook_performance_{today}.csv'
        merged_df.to_csv(output_file, index=False)
        print(f"Synced results saved to {output_file}")
        return True
            
    except Exception as e:
        print(f"Error during sync: {e}")
        return False

if __name__ == "__main__":
    sync_data()

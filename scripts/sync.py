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
        
        # Convert scores to numeric, replacing empty strings with NaN
        results_df['Home Score'] = pd.to_numeric(results_df['Home Score'], errors='coerce')
        results_df['Away Score'] = pd.to_numeric(results_df['Away Score'], errors='coerce')
        
        # Add winner column
        def determine_winner(row):
            if pd.isna(row['Home Score']) or pd.isna(row['Away Score']):
                return None
                
            home_odds = float(row['Home Team Odds'])
            away_odds = float(row['Away Team Odds'])
            
            if row['Home Score'] > row['Away Score']:
                return 'underdog' if home_odds > away_odds else 'favorite'
            elif row['Away Score'] > row['Home Score']:
                return 'underdog' if away_odds > home_odds else 'favorite'
            return 'Draw'
            
        # Merge odds data with results first
        merged_df = pd.merge(
            results_df,
            odds_df[['Sport', 'Match Date', 'Home Team', 'Away Team', 'Home Team Odds', 'Away Team Odds', 'Bookmaker', 'Compiled_At']],
            on=['Sport', 'Match Date', 'Home Team', 'Away Team'],
            how='outer'
        )
        
        # Drop rows without odds
        merged_df = merged_df.dropna(subset=['Home Team Odds', 'Away Team Odds'])
        
        # Now calculate winner based on merged data
        merged_df['Winner'] = merged_df.apply(determine_winner, axis=1)
        
        # Save all games, completed or not
        output_file = f'data/synced_results_{today}.csv'
        merged_df.to_csv(output_file, index=False)
        print(f"Synced results saved to {output_file}")
        return True
            
    except Exception as e:
        print(f"Error during sync: {e}")
        return False

if __name__ == "__main__":
    sync_data()
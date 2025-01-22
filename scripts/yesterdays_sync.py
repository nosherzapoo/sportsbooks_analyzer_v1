import pandas as pd
from datetime import datetime, timedelta
import os

def sync_yesterdays_data():
    try:
        # Get yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        print(f"Syncing data for date: {yesterday}")
        
        # Required files
        odds_file = f'data/game_odds_{yesterday}.csv'
        results_file = f'data/game_results_{yesterday}.csv'
        
        # Check if files exist
        if not os.path.exists(odds_file):
            raise FileNotFoundError(f"Missing odds file: {odds_file}")
        if not os.path.exists(results_file):
            raise FileNotFoundError(f"Missing results file: {results_file}")
            
        print(f"Found required files:\n- {odds_file}\n- {results_file}")
        
        # Read the files
        odds_df = pd.read_csv(odds_file)
        results_df = pd.read_csv(results_file)
        
        print(f"Loaded {len(odds_df)} odds records and {len(results_df)} results records")
        
        # Debug print before merge
        print("\nSample of odds data:")
        print(odds_df[['Sport', 'Home Team', 'Away Team']].head())
        print("\nSample of results data:")
        print(results_df[['Sport', 'Home Team', 'Away Team']].head())
        
        # Ensure all columns used in merge are strings
        merge_columns = ['Sport', 'Home Team', 'Away Team']
        for col in merge_columns:
            odds_df[col] = odds_df[col].astype(str).str.strip().str.lower()
            results_df[col] = results_df[col].astype(str).str.strip().str.lower()
        
        # Convert scores to numeric, replacing empty strings with NaN
        results_df['Home Score'] = pd.to_numeric(results_df['Home Score'], errors='coerce')
        results_df['Away Score'] = pd.to_numeric(results_df['Away Score'], errors='coerce')
        
        # Add winner column
        def determine_winner(row):
            try:
                if pd.isna(row['Home Score']) or pd.isna(row['Away Score']):
                    return None
                    
                home_odds = float(row['Home Team Odds'])
                away_odds = float(row['Away Team Odds'])
                
                if row['Home Score'] > row['Away Score']:
                    return 'underdog' if home_odds > away_odds else 'favorite'
                elif row['Away Score'] > row['Home Score']:
                    return 'underdog' if away_odds > home_odds else 'favorite'
                return 'Draw'
            except Exception as e:
                print(f"Error determining winner for row: {row}")
                return None
            
        # Merge odds data with results, only using Sport and team names
        print("\nPerforming merge operation...")
        merged_df = pd.merge(
            results_df,
            odds_df[['Sport', 'Home Team', 'Away Team', 'Home Team Odds', 'Away Team Odds', 'Bookmaker', 'Compiled_At']],
            on=['Sport', 'Home Team', 'Away Team'],
            how='inner'
        )
        
        print(f"\nMerged data contains {len(merged_df)} records")
        
        if len(merged_df) == 0:
            print("\nNo matching records found! Checking for potential mismatches:")
            print("\nUnique sports in odds:", odds_df['Sport'].unique())
            print("Unique sports in results:", results_df['Sport'].unique())
            print("\nSample teams in odds:")
            print(odds_df[['Sport', 'Home Team', 'Away Team']].head(10))
            print("\nSample teams in results:")
            print(results_df[['Sport', 'Home Team', 'Away Team']].head(10))
            return False
        
        # Calculate winner based on merged data
        merged_df['Winner'] = merged_df.apply(determine_winner, axis=1)
        
        # Count results by winner type
        winner_counts = merged_df['Winner'].value_counts()
        print("\nWinner distribution:")
        print(winner_counts)
        
        # Save all games, completed or not
        output_file = f'data/sportsbook_performance_{yesterday}.csv'
        merged_df.to_csv(output_file, index=False)
        print(f"\nSynced results saved to {output_file}")
        return True
            
    except Exception as e:
        print(f"Error during sync: {e}")
        print("\nDebugging information:")
        if 'odds_df' in locals():
            print("Sports in odds data:", odds_df['Sport'].unique())
            print("Sample teams in odds:")
            print(odds_df[['Sport', 'Home Team', 'Away Team']].head())
        if 'results_df' in locals():
            print("Sports in results data:", results_df['Sport'].unique())
            print("Sample teams in results:")
            print(results_df[['Sport', 'Home Team', 'Away Team']].head())
        return False

if __name__ == "__main__":
    sync_yesterdays_data() 
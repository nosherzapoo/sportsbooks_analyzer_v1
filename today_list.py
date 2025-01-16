import pandas as pd
from datetime import datetime

# Read the CSV file
df = pd.read_csv('compiled_odds.csv')

# Convert date strings to datetime objects
df['Match Date'] = pd.to_datetime(df['Match Date'], format='%b %d, %Y, %I:%M %p')

# Get today's date
today = datetime.now().date()

# Filter for games happening today
today_games = df[df['Match Date'].dt.date == today]

# Get unique games (remove duplicate rows for different bookmakers)
today_unique = today_games.groupby(['Sport', 'Match Date', 'Home Team', 'Away Team']).first().reset_index()

# Sort by date/time
today_unique = today_unique.sort_values('Match Date')

# Format date back to string for CSV
today_unique['Match Date'] = today_unique['Match Date'].dt.strftime('%b %d, %Y, %I:%M %p')

# Save to CSV
today = datetime.now().strftime('%Y%m%d')
today_unique.to_csv(f'game_odds_{today}.csv', index=False)

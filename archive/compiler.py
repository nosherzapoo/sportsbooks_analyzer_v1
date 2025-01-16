import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

def download_odds_html(url):
    try:
        full_url = f"https://sportsbook-odds-comparer.vercel.app{url}"
        response = requests.get(full_url)
        response.raise_for_status()
        html = response.text
        return html
    except requests.RequestException as e:
        print(f"Error downloading odds: {e}")
        return None

def parse_html_to_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    games = soup.find_all('div', class_='m-5 flex flex-col shadow-lg')
    
    all_data = []
    for game in games:
        match_title = game.find('h2', class_='text-3xl').text
        match_date = game.find('p', class_='text-cyan-700 text-sm').text
        
        # Convert UTC time to EST
        try:
            # Parse the UTC time
            utc_time = datetime.strptime(match_date, "%b %d, %Y, %I:%M %p")
            utc_time = utc_time.replace(tzinfo=ZoneInfo('UTC'))
            
            # Convert to EST
            est_time = utc_time.astimezone(ZoneInfo('America/New_York'))
            match_date = est_time.strftime("%b %d, %Y, %I:%M %p")
        except Exception as e:
            print(f"Error converting time: {e}")
            # Keep original time if conversion fails
            pass
        
        teams = match_title.split(' vs ')
        home_team = teams[0].strip()
        away_team = teams[1].strip()
        
        odds_sections = game.find_all('div', class_='p-3')
        for odds_section in odds_sections:
            team_name = odds_section.find('span').text.strip()
            odds_items = odds_section.find_all('div', class_='grid grid-flow-row p-3')
            
            for odds_item in odds_items:
                price = odds_item.find('span').text.strip()
                bookmaker = odds_item.find('span', class_='text-xl').text.strip()
                
                all_data.append({
                    'Match Date': match_date,
                    'Home Team': home_team,
                    'Away Team': away_team,
                    'Team': team_name,
                    'Price': price,
                    'Bookmaker': bookmaker
                })
    
    return pd.DataFrame(all_data)

def clean_table(df, sport):
    cleaned_df = pd.DataFrame()
    cleaned_df['Sport'] = sport
    
    unique_matches = df[['Match Date', 'Home Team', 'Away Team']].drop_duplicates()
    
    match_dates = []
    home_teams = []
    away_teams = []
    home_odds = []
    away_odds = []
    bookmakers = []
    sports = []
    
    def american_to_decimal(american_odds):
        american = int(american_odds.replace(' ML', ''))
        if american > 0:
            return round(american/100 + 1, 3)
        else:
            return round(100/abs(american) + 1, 3)
    
    for _, match in unique_matches.iterrows():
        match_data = df[
            (df['Match Date'] == match['Match Date']) & 
            (df['Home Team'] == match['Home Team']) &
            (df['Away Team'] == match['Away Team'])
        ]
        
        for bookmaker in match_data['Bookmaker'].unique():
            match_odds = match_data[match_data['Bookmaker'] == bookmaker]
            
            if len(match_odds) == 2:
                home_team_odds = american_to_decimal(match_odds[match_odds['Team'] == match['Home Team']]['Price'].iloc[0])
                away_team_odds = american_to_decimal(match_odds[match_odds['Team'] == match['Away Team']]['Price'].iloc[0])
                
                match_dates.append(match['Match Date'])
                home_teams.append(match['Home Team'])
                away_teams.append(match['Away Team'])
                home_odds.append(home_team_odds)
                away_odds.append(away_team_odds)
                bookmakers.append(bookmaker)
                sports.append(sport)
    
    cleaned_df = pd.DataFrame({
        'Sport': sports,
        'Match Date': match_dates,
        'Home Team': home_teams,
        'Away Team': away_teams,
        'Home Team Odds': home_odds,
        'Away Team Odds': away_odds,
        'Bookmaker': bookmakers
    })
    
    return cleaned_df

# Read sports URLs
sports_df = pd.read_csv('sports_url.csv')

# Process all sports
all_cleaned_data = []
for _, row in sports_df.iterrows():
    sport = row['Sport']
    url = row['URL']
    
    print(f"Processing {sport} odds...")
    
    # Download and parse HTML
    html_content = download_odds_html(url)
    if html_content:
        # Convert to initial table
        raw_df = parse_html_to_table(html_content)
        
        # Only process if there are entries
        if not raw_df.empty:
            # Clean the table
            cleaned_sport_df = clean_table(raw_df, sport)
            all_cleaned_data.append(cleaned_sport_df)
        else:
            print(f"No entries found for {sport}, skipping...")

# Combine all data if we have any
if all_cleaned_data:
    final_df = pd.concat(all_cleaned_data, ignore_index=True)
    # Save to CSV
    final_df.to_csv('compiled_odds.csv', index=False)
    print("Compiled odds data saved to compiled_odds.csv")
else:
    print("No data found for any sports")

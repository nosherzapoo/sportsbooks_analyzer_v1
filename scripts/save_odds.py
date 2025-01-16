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
            utc_time = datetime.strptime(match_date, "%b %d, %Y, %I:%M %p")
            utc_time = utc_time.replace(tzinfo=ZoneInfo('UTC'))
            est_time = utc_time.astimezone(ZoneInfo('America/New_York'))
            match_date = est_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error converting time: {e}")
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
    def american_to_decimal(american_odds):
        american = int(american_odds.replace(' ML', ''))
        if american > 0:
            return round(american/100 + 1, 3)
        else:
            return round(100/abs(american) + 1, 3)
    
    cleaned_data = []
    
    for _, match in df[['Match Date', 'Home Team', 'Away Team']].drop_duplicates().iterrows():
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
                
                cleaned_data.append({
                    'Sport': sport,
                    'Match Date': match['Match Date'],
                    'Home Team': match['Home Team'],
                    'Away Team': match['Away Team'],
                    'Home Team Odds': home_team_odds,
                    'Away Team Odds': away_team_odds,
                    'Bookmaker': bookmaker
                })
    
    return pd.DataFrame(cleaned_data)

def save_daily_odds():
    # Read sports URLs
    sports_df = pd.read_csv('data/sports_url.csv')
    current_date = datetime.now().strftime('%Y%m%d')
    today = datetime.now().date()
    
    all_cleaned_data = []
    
    for _, row in sports_df.iterrows():
        sport = row['Sport']
        url = row['URL']
        
        print(f"Processing {sport} odds...")
        
        html_content = download_odds_html(url)
        if html_content:
            raw_df = parse_html_to_table(html_content)
            
            if not raw_df.empty:
                # Convert Match Date to datetime
                raw_df['Match Date'] = pd.to_datetime(raw_df['Match Date'])
                # Filter for today's games only
                raw_df = raw_df[raw_df['Match Date'].dt.date == today]
                
                if not raw_df.empty:
                    cleaned_sport_df = clean_table(raw_df, sport)
                    all_cleaned_data.append(cleaned_sport_df)
                else:
                    print(f"No games today for {sport}, skipping...")
            else:
                print(f"No entries found for {sport}, skipping...")

    if all_cleaned_data:
        final_df = pd.concat(all_cleaned_data, ignore_index=True)
        # Add compilation timestamp
        final_df['Compiled_At'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f'data/game_odds_{current_date}.csv'
        final_df.to_csv(filename, index=False)
        print(f"Today's odds data saved to {filename}")
    else:
        print("No games found for today")

if __name__ == "__main__":
    save_daily_odds() 
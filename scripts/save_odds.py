import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging
import os
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_odds_html(url):
    try:
        full_url = f"https://sportsbook-odds-comparer.vercel.app{url}"
        response = requests.get(full_url)
        response.raise_for_status()
        html = response.text
        return html
    except requests.RequestException as e:
        logger.error(f"Error downloading odds: {e}")
        return None

def parse_html_to_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    games = soup.find_all('div', class_='m-5 flex flex-col shadow-lg')
    
    logger.info(f"Found {len(games)} games in HTML content")
    
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
            logger.error(f"Error converting time for {match_title}: {e}")
            pass
        
        teams = match_title.split(' vs ')
        home_team = teams[0].strip()
        away_team = teams[1].strip()
        
        logger.info(f"Processing match: {home_team} vs {away_team} on {match_date} (EST)")
        
        # Find all team spans (directly inside the game div or inside nested divs)
        team_spans = game.find_all('span', recursive=True)
        
        for i, span in enumerate(team_spans):
            # Skip spans that are inside grid-flow-row (these are the odds and bookmakers)
            if span.find_parent('div', class_='grid grid-flow-row p-3'):
                continue
                
            team_name = span.text.strip()
            
            # For each team, find its odds container (the div after the span)
            odds_container = span.find_next('div', class_='flex flex-row justify-around p-6 bg-white flex-wrap')
            if not odds_container:
                continue
                
            odds_items = odds_container.find_all('div', class_='grid grid-flow-row p-3')
            
            logger.info(f"Found {len(odds_items)} odds entries for {team_name}")
            
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
        try:
            american = int(american_odds.replace(' ML', ''))
            if american > 0:
                return round(american/100 + 1, 3)
            else:
                return round(100/abs(american) + 1, 3)
        except Exception as e:
            logger.error(f"Error converting odds '{american_odds}': {e}")
            return None
    
    cleaned_data = []
    
    # Define sports that can have draws
    draw_sports = {
        'Primera División - Argentina', 'A-League', 'Austrian Football Bundesliga', 
        'Belgium First Div', 'Copa Libertadores', 'Denmark Superliga', 'Championship', 
        'EFL Cup', 'League 1', 'League 2', 'EPL', 'FA Cup', 'Ligue 1 - France', 
        'Ligue 2 - France', 'Bundesliga - Germany', 'Bundesliga 2 - Germany', 
        '3. Liga - Germany', 'Super League - Greece', 'Serie A - Italy', 
        'Serie B - Italy', 'League of Ireland', 'Liga MX', 'Dutch Eredivisie', 
        'Primeira Liga - Portugal', 'La Liga - Spain', 'La Liga 2 - Spain', 
        'Premiership - Scotland', 'Swiss Superleague', 'Turkey Super League', 
        'UEFA Champions League', 'UEFA Europa Conference League', 'UEFA Europa League'
    }
    unique_matches = df[['Match Date', 'Home Team', 'Away Team']].drop_duplicates()
    
    for _, match in unique_matches.iterrows():
        match_data = df[
            (df['Match Date'] == match['Match Date']) & 
            (df['Home Team'] == match['Home Team']) &
            (df['Away Team'] == match['Away Team'])
        ]
        
        for bookmaker in match_data['Bookmaker'].unique():
            match_odds = match_data[match_data['Bookmaker'] == bookmaker]
            
            # Check if number of odds entries is valid for the sport
            expected_odds = 3 if sport in draw_sports else 2
            if len(match_odds) != expected_odds:
                logger.warning(f"Skipping {bookmaker} for {match['Home Team']} vs {match['Away Team']} - "
                             f"expected {expected_odds} odds entries, found {len(match_odds)}")
                continue
            
            try:
                home_odds = match_odds[match_odds['Team'] == match['Home Team']]['Price'].iloc[0]
                away_odds = match_odds[match_odds['Team'] == match['Away Team']]['Price'].iloc[0]
                
                home_team_odds = american_to_decimal(home_odds)
                away_team_odds = american_to_decimal(away_odds)
                
                # Create base entry
                entry = {
                    'Sport': sport,
                    'Match Date': match['Match Date'],
                    'Home Team': match['Home Team'],
                    'Away Team': match['Away Team'],
                    'Home Team Odds': home_team_odds,
                    'Away Team Odds': away_team_odds,
                    'Bookmaker': bookmaker
                }
                
                # Add draw odds for sports that can have draws
                if sport in draw_sports and expected_odds == 3:
                    # Find the draw entry (not home team and not away team)
                    draw_entry = match_odds[
                        (match_odds['Team'] != match['Home Team']) & 
                        (match_odds['Team'] != match['Away Team'])
                    ]
                    
                    if not draw_entry.empty:
                        draw_odds = draw_entry['Price'].iloc[0]
                        draw_odds_decimal = american_to_decimal(draw_odds)
                        entry['Draw Odds'] = draw_odds_decimal
                    else:
                        logger.warning(f"Draw odds not found for {match['Home Team']} vs {match['Away Team']} with {bookmaker}")
                
                if home_team_odds and away_team_odds:
                    cleaned_data.append(entry)
            except Exception as e:
                logger.error(f"Error processing odds for {bookmaker} in {match['Home Team']} vs {match['Away Team']}: {e}")
                continue
    
    return pd.DataFrame(cleaned_data)

def save_daily_odds():
    # Read sports URLs
    sports_df = pd.read_csv('data/sports_url.csv')
    
    # Use EST timezone for all date operations
    est_tz = ZoneInfo('America/New_York')
    current_date_est = datetime.now(est_tz)
    current_date_str = current_date_est.strftime('%Y%m%d')
    
    # Get tomorrow's date for filtering (in EST)
    tomorrow_est = (current_date_est + timedelta(days=1)).date()
    tomorrow_date_str = tomorrow_est.strftime('%Y%m%d')
    
    logger.info(f"Processing odds for tomorrow's date: {tomorrow_est} (EST)")
    
    all_cleaned_data = []
    
    for _, row in sports_df.iterrows():
        sport = row['Sport']
        url = row['URL']
        
        logger.info(f"Processing {sport} odds from {url}...")
        
        html_content = download_odds_html(url)
        if html_content:
            raw_df = parse_html_to_table(html_content)
            
            if not raw_df.empty:
                # Convert Match Date to datetime (already in EST from parse_html_to_table)
                raw_df['Match Date'] = pd.to_datetime(raw_df['Match Date'])
                
                # Filter for tomorrow's games only (EST)
                filtered_df = raw_df[raw_df['Match Date'].dt.date == tomorrow_est]
                
                logger.info(f"Found {len(raw_df)} total entries, {len(filtered_df)} entries for tomorrow (EST)")
                
                if not filtered_df.empty:
                    cleaned_sport_df = clean_table(filtered_df, sport)
                    logger.info(f"Cleaned data for {sport}: {len(cleaned_sport_df)} entries")
                    all_cleaned_data.append(cleaned_sport_df)
                else:
                    logger.warning(f"No games tomorrow for {sport}, skipping...")
            else:
                logger.warning(f"No entries found for {sport}, skipping...")
        else:
            logger.error(f"Failed to download HTML content for {sport}")

    if all_cleaned_data:
        final_df = pd.concat(all_cleaned_data, ignore_index=True)
        # Add compilation timestamp in EST
        final_df['Compiled_At'] = datetime.now(est_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"Total compiled odds entries: {len(final_df)}")
        
        # Save with tomorrow's date
        tomorrow_filename = f'data/game_odds_{tomorrow_date_str}.csv'
        final_df.to_csv(tomorrow_filename, index=False)
        logger.info(f"Tomorrow's odds data saved to {tomorrow_filename} (EST)")
    else:
        logger.warning("No games found for tomorrow (EST)")

if __name__ == "__main__":
    save_daily_odds() 

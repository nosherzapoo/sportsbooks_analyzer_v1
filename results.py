import pandas as pd
import requests
import csv
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

def get_todays_game_results():
    # Load environment variables
    load_dotenv()
    
    # API endpoint and key 
    API_KEY = os.getenv('ODDS_API_KEY')
    BASE_URL = 'https://api.the-odds-api.com/v4'
    
    try:
        # Read today's games list
        today = datetime.now().strftime('%Y%m%d')
        today_games = pd.read_csv(f'game_odds_{today}.csv')
        
        # Create CSV file with today's date
        today = datetime.now().strftime('%Y%m%d')
        filename = f'game_results_{today}.csv'
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Sport', 'Event Time', 'Home Team', 'Away Team', 
                         'Home Score', 'Away Score', 'Status', 'Game ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Get unique sports from today's games
            unique_sports = today_games['Sport'].unique()
            
            # Map sports to API keys
            sport_key_map = {
                'NFL': 'americanfootball_nfl',
                'NCAAF': 'americanfootball_ncaaf',
                'CFL': 'americanfootball_cfl',
                'UFL': 'americanfootball_ufl',
                'AFL': 'aussierules_afl',
                'MLB': 'baseball_mlb',
                'Basketball Euroleague': 'basketball_euroleague',
                'NBA': 'basketball_nba',
                'WNBA': 'basketball_wnba',
                'NCAAB': 'basketball_ncaab',
                'WNCAAB': 'basketball_wncaab',
                'NBL': 'basketball_nbl',
                'Boxing': 'boxing_boxing',
                'Big Bash': 'cricket_big_bash',
                'Test Matches': 'cricket_test_match',
                'NHL': 'icehockey_nhl',
                'SHL': 'icehockey_sweden_hockey_league',
                'MMA': 'mma_mixed_martial_arts',
                'NRL': 'rugbyleague_nrl',
                'Primera División - Argentina': 'soccer_argentina_primera_division',
                'A-League': 'soccer_australia_aleague',
                'Austrian Football Bundesliga': 'soccer_austria_bundesliga',
                'Belgium First Div': 'soccer_belgium_first_div',
                'Brazil Série A': 'soccer_brazil_campeonato',
                'Brazil Série B': 'soccer_brazil_serie_b',
                'Primera División - Chile': 'soccer_chile_campeonato',
                'Super League - China': 'soccer_china_superleague',
                'Denmark Superliga': 'soccer_denmark_superliga',
                'Championship': 'soccer_efl_champ',
                'EFL Cup': 'soccer_england_efl_cup',
                'League 1': 'soccer_england_league1',
                'League 2': 'soccer_england_league2',
                'EPL': 'soccer_epl',
                'FA Cup': 'soccer_fa_cup',
                'FIFA World Cup': 'soccer_fifa_world_cup',
                'Veikkausliiga - Finland': 'soccer_finland_veikkausliiga',
                'Ligue 1 - France': 'soccer_france_ligue_one',
                'Ligue 2 - France': 'soccer_france_ligue_two',
                'Bundesliga - Germany': 'soccer_germany_bundesliga',
                'Bundesliga 2 - Germany': 'soccer_germany_bundesliga2',
                '3. Liga - Germany': 'soccer_germany_liga3',
                'Super League - Greece': 'soccer_greece_super_league',
                'Serie A - Italy': 'soccer_italy_serie_a',
                'Serie B - Italy': 'soccer_italy_serie_b',
                'J League': 'soccer_japan_j_league',
                'K League 1': 'soccer_korea_kleague1',
                'League of Ireland': 'soccer_league_of_ireland',
                'Liga MX': 'soccer_mexico_ligamx',
                'Dutch Eredivisie': 'soccer_netherlands_eredivisie',
                'Eliteserien - Norway': 'soccer_norway_eliteserien',
                'Ekstraklasa - Poland': 'soccer_poland_ekstraklasa',
                'Primeira Liga - Portugal': 'soccer_portugal_primeira_liga',
                'La Liga - Spain': 'soccer_spain_la_liga',
                'La Liga 2 - Spain': 'soccer_spain_segunda_division',
                'Premiership - Scotland': 'soccer_spl',
                'Allsvenskan - Sweden': 'soccer_sweden_allsvenskan',
                'Superettan - Sweden': 'soccer_sweden_superettan',
                'Swiss Superleague': 'soccer_switzerland_superleague',
                'Turkey Super League': 'soccer_turkey_super_league',
                'UEFA Europa Conference League': 'soccer_uefa_europa_conference_league',
                'UEFA Champions League': 'soccer_uefa_champs_league',
                'UEFA Champions League Qualification': 'soccer_uefa_champs_league_qualification',
                'UEFA Europa League': 'soccer_uefa_europa_league',
                'UEFA Euro 2024': 'soccer_uefa_european_championship',
                'UEFA Euro Qualification': 'soccer_uefa_euro_qualification',
                'Copa América': 'soccer_conmebol_copa_america',
                'Copa Libertadores': 'soccer_conmebol_copa_libertadores',
                'MLS': 'soccer_usa_mls',
                'ATP Australian Open': 'tennis_atp_aus_open_singles',
                'ATP Canadian Open': 'tennis_atp_canadian_open',
                'ATP China Open': 'tennis_atp_china_open',
                'ATP Cincinnati Open': 'tennis_atp_cincinnati_open',
                'ATP French Open': 'tennis_atp_french_open',
                'ATP Paris Masters': 'tennis_atp_paris_masters',
                'ATP Shanghai Masters': 'tennis_atp_shanghai_masters',
                'ATP US Open': 'tennis_atp_us_open',
                'ATP Wimbledon': 'tennis_atp_wimbledon',
                'WTA Australian Open': 'tennis_wta_aus_open_singles',
                'WTA Canadian Open': 'tennis_wta_canadian_open',
                'WTA China Open': 'tennis_wta_china_open',
                'WTA Cincinnati Open': 'tennis_wta_cincinnati_open',
                'WTA French Open': 'tennis_wta_french_open',
                'WTA US Open': 'tennis_wta_us_open',
                'WTA Wimbledon': 'tennis_wta_wimbledon',
                'WTA Wuhan Open': 'tennis_wta_wuhan_open'
            }
            
            # Get scores for each sport
            for sport in unique_sports:
                try:
                    if sport not in sport_key_map:
                        print(f"No API key mapping found for {sport}, skipping...")
                        continue
                        
                    sport_key = sport_key_map[sport]
                    scores_url = f'{BASE_URL}/sports/{sport_key}/scores/?daysFrom=1&apiKey={API_KEY}'
                    print(f"\nScraping scores for {sport} from: {scores_url}")
                    
                    scores_response = requests.get(scores_url, verify=False)
                    scores_response.raise_for_status()
                    scores_data = scores_response.json()
                    
                    # Filter for games in today's list
                    today_teams = set(today_games[today_games['Sport'] == sport]['Home Team'].tolist() + 
                                    today_games[today_games['Sport'] == sport]['Away Team'].tolist())
                    
                    for game in scores_data:
                        if game['home_team'] in today_teams or game['away_team'] in today_teams:
                            scores = game.get('scores', {})
                            home_score = ''
                            away_score = ''
                            if scores:
                                for score in scores:
                                    if score['name'] == game['home_team']:
                                        home_score = score.get('score', '')
                                    elif score['name'] == game['away_team']:
                                        away_score = score.get('score', '')
                                        
                            row_data = {
                                'Sport': game['sport_title'],
                                'Event Time': game['commence_time'],
                                'Home Team': game['home_team'],
                                'Away Team': game['away_team'],
                                'Home Score': home_score,
                                'Away Score': away_score,
                                'Status': game.get('completed', False) and 'Completed' or game.get('status', 'Scheduled'),
                                'Game ID': game['id']
                            }
                            writer.writerow(row_data)

                except Exception as e:
                    print(f"Error scraping {sport}: {str(e)}")
                    continue
        
        return filename

    except Exception as e:
        print(f"Error fetching game results: {str(e)}")
        return None

if __name__ == "__main__":
    get_todays_game_results()

import pandas as pd
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_game_results(sport, sport_url):
    api_key = os.getenv('ODDS_API_KEY')
    
    base_url = "https://api.the-odds-api.com/v4/sports/{url}/scores/"
    
    try:
        response = requests.get(
            base_url.format(url=sport_url),
            params={
                'apiKey': api_key,
                'daysFrom': 1
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching results for {sport}: {e}")
        return None

def process_results():
    try:
        today = datetime.now().strftime('%Y%m%d')
        
        # Read today's odds file to get active leagues
        odds_file = f'data/game_odds_20250310.csv'
        if not os.path.exists(odds_file):
            raise FileNotFoundError(f"Could not find odds file: {odds_file}")
            
        odds_df = pd.read_csv(odds_file)
        
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
        
        results = []
        # Get unique sports from odds file
        active_sports = odds_df['Sport'].unique()
        
        for sport in active_sports:
            # Get URL for this sport
            sport_url = sport_key_map.get(sport)
            if sport_url:
                api_results = fetch_game_results(sport, sport_url)
                
                if api_results:
                    # Get games for this sport from odds file
                    sport_games = odds_df[odds_df['Sport'] == sport]
                    
                    for match in api_results:
                        # Check if this game exists in our odds data
                        if any((match['home_team'] == game['Home Team'] and 
                               match['away_team'] == game['Away Team']) 
                               for _, game in sport_games.iterrows()):
                            
                            result = {
                                'Sport': sport,
                                'Match Date': datetime.now().strftime('%Y-%m-%d'),
                                'Home Team': match['home_team'],
                                'Away Team': match['away_team'],
                                'Home Score': None,
                                'Away Score': None,
                                'Status': 'Completed' if match.get('completed') else 'Unknown',
                                'Game ID': match['id']
                            }
                            
                            if match.get('completed') and match.get('scores'):
                                for score in match['scores']:
                                    if score['name'] == match['home_team']:
                                        result['Home Score'] = score['score']
                                    elif score['name'] == match['away_team']:
                                        result['Away Score'] = score['score']
                                
                            results.append(result)
        
        if results:
            results_df = pd.DataFrame(results)
            
            output_file = f'data/game_results_{today}.csv'
            results_df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")
            
            return True
            
    except Exception as e:
        print(f"Error processing results: {e}")
        print("\nDebugging information:")
        if 'odds_df' in locals():
            print("Active sports found:", active_sports)
        return False

if __name__ == "__main__":
    process_results()
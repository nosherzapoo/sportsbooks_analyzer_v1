from bs4 import BeautifulSoup
import pandas as pd

# Load the HTML content (assume the HTML content is stored in a string named html_content)
with open('odds.html', 'r', encoding='utf-8') as f:
    html_content = f.read()
soup = BeautifulSoup(html_content, 'html.parser')

# Find all games
games = soup.find_all('div', class_='m-5 flex flex-col shadow-lg')

# Initialize a list to store data
all_data = []

# Iterate over each game to extract data
for game in games:
    # Extract teams and match details
    match_title = game.find('h2', class_='text-3xl').text
    match_date = game.find('p', class_='text-cyan-700 text-sm').text

    teams = match_title.split(' vs ')
    home_team = teams[0].strip()
    away_team = teams[1].strip()

    # Extract odds for each team
    odds_sections = game.find_all('div', class_='p-3')
    
    for odds_section in odds_sections:
        team_name = odds_section.find('span').text.strip()
        odds_items = odds_section.find_all('div', class_='grid grid-flow-row p-3')

        for odds_item in odds_items:
            price = odds_item.find('span').text.strip()
            bookmaker = odds_item.find('span', class_='text-xl').text.strip()

            # Add to the data list
            all_data.append({
                'Match Date': match_date,
                'Home Team': home_team,
                'Away Team': away_team,
                'Team': team_name,
                'Price': price,
                'Bookmaker': bookmaker
            })

# Convert to a DataFrame
df = pd.DataFrame(all_data)

# Save to a CSV file or display the table
csv_file = "sportsbook_odds.csv"
df.to_csv(csv_file, index=False)
print(f"Data saved to {csv_file}")

# Display the DataFrame (for verification)
print(df)

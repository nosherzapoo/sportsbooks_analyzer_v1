import requests

def download_odds_html():
    url = "https://sportsbook-odds-comparer.vercel.app/odds/americanfootball_nfl/moneyline"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        html = response.text
        with open('odds.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("HTML content has been saved to odds.html")
        return html
    except requests.RequestException as e:
        print(f"Error downloading odds: {e}")  # Print error message
        return None

# Call the function
download_odds_html()

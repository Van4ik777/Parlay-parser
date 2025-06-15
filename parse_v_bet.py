import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

driver_path = r'C:\Users\user\PycharmProjects\stavki\chrome_driver\chromedriver.exe'
service = Service(driver_path)

driver = webdriver.Chrome(service=service)
driver.maximize_window()

url = 'https://www.vbet.ua/uk/sports/pre-match/event-view/Soccer/France/548/'
driver.get(url)

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'root'))
    )
    time.sleep(20)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    market_header = soup.find('p', class_='sgm-market-g-h-title-bc ellipsis', title="Тотал голів")

    if market_header:
        parent_div = market_header.find_parent('div', class_='sgm-market-g')
        if parent_div and 'sgm-market-g-h-title-bc' in market_header['class'] and market_header['title'] == "Тотал голів":
            print(parent_div)
            matches = driver.find_elements(By.CLASS_NAME, 'multi-column-teams')
            team_names = [match.text.strip() for match in matches]
            print(f"Команды: {team_names}")

            totals_data = []
            for match in matches:
                ActionChains(driver).move_to_element(match).perform()
                match.click()
                time.sleep(5)

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                market_header = soup.find('p', class_='sgm-market-g-h-title-bc ellipsis', title="Тотал голів")
                parent_div = market_header.find_parent('div', class_='sgm-market-g')

                game_details_section = soup.find('div', class_='game-details-section')
                time_element = game_details_section.find('time') if game_details_section else None
                game_time = time_element.text.strip() if time_element else None
                if game_time:
                    game_time = ''.join(filter(str.isdigit, game_time.split(':')[0]))[:2]

                market_items = parent_div.find_all('div', class_='sgm-market-g-i-cell-bc market-bc')
                match_totals = {
                    'team1': '',
                    'team2': '',
                    'totals': []
                }

                team_lines = match.text.strip().split('\n')
                if len(team_lines) >= 2:
                    match_totals['team1'] = team_lines[0].replace("ФК", "").replace("АФК", "").replace("ФКА", "").strip().lower()
                    match_totals['team2'] = team_lines[1].replace("ФК", "").replace("АФК", "").replace("ФКА", "").strip().lower()

                i = 0
                for item in market_items:
                    market_name_tag = item.find('span', class_='market-name-bc ellipsis')
                    if market_name_tag:
                        market_name = market_name_tag.text.strip()
                        odds_tag = item.find('span', class_='market-odd-bc')
                        if i % 2 == 0:
                            i += 1
                            bet_type = 'більше'
                        else:
                            i += 1
                            bet_type = "менше"
                        if odds_tag:
                            odds = odds_tag.text.strip()
                            match_totals['totals'].append({
                                'market': market_name,
                                'odds': odds,
                                'type': bet_type
                            })

                totals_data.append({
                    'team1': match_totals['team1'],
                    'team2': match_totals['team2'],
                    'game_time': game_time,
                    'totals': match_totals['totals']
                })

            game_info = {
                "matches": totals_data,
            }

            with open('matches_v_bet.json', 'w', encoding='utf-8') as json_file:
                json.dump(game_info, json_file, ensure_ascii=False, indent=4)
        else:
            print("Parent div does not contain the required class or title")
    else:
        print("Не найден элемент с title 'Тотал голів'")

finally:
    driver.quit()

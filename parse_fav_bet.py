import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

driver_path = r'C:\Users\user\PycharmProjects\stavki\chrome_driver\chromedriver.exe'
service = Service(driver_path)

driver = webdriver.Chrome(service=service)
driver.maximize_window()

url = 'https://www.favbet.ua/uk/sports/tournament/soccer/17351/'
driver.get(url)

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'root'))
    )
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    event_elements = soup.find_all(attrs={"data-role": True})

    event_ids = [re.sub(r'\D', '', event.get('data-role')) for event in event_elements if
                 event.get('data-role') and event.get('data-role').startswith('event-id')]

    print(f"Найденные event-id (только цифры): {event_ids}")
    matches_data = []

    for event_id in event_ids:
        try:
            event_url = f'https://www.favbet.ua/uk/sports/event/soccer/{event_id}/'
            print(f"Переход по ссылке: {event_url}")

            driver.get(event_url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'root'))
            )
            main_filter = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Основні')]"))
            )
            main_filter.click()
            time.sleep(5)
            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')

            clubs = soup.find_all(class_="sr-lmt-plus-scb__team-name")
            game_time_div = soup.find('div', class_='sr-lmt-plus-scb__status srt-text-secondary srt-neutral-9')

            game_time = game_time_div.find('div', class_='srm-is-uppercase').get_text(
                strip=True) if game_time_div else "Не указано"

            if game_time != "Не указано":
                game_time = ''.join(re.findall(r'\d+', game_time)[:2])

            team1 = clubs[0].get_text(strip=True).replace("ФК", "").replace("АФК", "").strip().lower() if len(clubs) > 0 else "unknown"
            team2 = clubs[1].get_text(strip=True).replace("ФК", "").replace("АФК", "").strip().lower() if len(clubs) > 1 else "unknown"

            totals = []
            main_blocks = soup.find_all(
                class_="Box_box--BuJ MarketsGroup_accordionContainer--vrs MarketsGroup_table--_Rp")

            for block in main_blocks:
                total_text = block.find(
                    class_="Text_base--RfU Text_general--tM6 Text_f_l--erO Text_left--lRL Text_l_normal--AeR")
                if total_text and "Тотал" == total_text.get_text(strip=True):
                    outcomes = block.find_all(class_="OutcomeButton_outcomeName--Knq")
                    coefficients = block.find_all(class_="OutcomeButton_coef--Ktw")

                    for outcome, coefficient in zip(outcomes, coefficients):
                        match = re.search(r'(\d+(\.\d+)?)', outcome.get_text(strip=True))
                        market = match.group(1) if match else "N/A"
                        market = market.rstrip('.0')

                        outcome_text = outcome.get_text(strip=True).lower()
                        if "більше" in outcome_text:
                            outcome_text = "більше"
                        elif "менше" in outcome_text:
                            outcome_text = "менше"

                        totals.append({
                            "market": market,
                            "odds": coefficient.get_text(strip=True),
                            "type": outcome_text
                        })

            matches_data.append({
                "team1": team1,
                "team2": team2,
                "game_time": game_time,
                "totals": totals
            })

        except Exception as e:
            print(f"Ошибка при работе с событием {event_id}: {e}")

    with open('matches_fav_bet_chempliga.json', 'w', encoding='utf-8') as json_file:
        json.dump({"matches": matches_data}, json_file, ensure_ascii=False, indent=4)

finally:
    driver.quit()

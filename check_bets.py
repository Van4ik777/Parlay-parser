import json

def load_matches_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_win(stake, odds):
    return round(stake * odds, 2)

def calculate_arbitrage_bet(odds1, odds2, total_bank):
    if (1 / odds1 + 1 / odds2) < 1:
        stake_1 = round(total_bank / (1 / odds1 + 1 / odds2) * (1 / odds1), 2)
        stake_2 = round(total_bank / (1 / odds1 + 1 / odds2) * (1 / odds2), 2)

        return stake_1, stake_2
    else:
        return None, None

def compare_bets_and_calculate(matches_1, matches_2, total_bank):
    results = []
    for match_1 in matches_1:
        for match_2 in matches_2:
            if (match_1['team1'] == match_2['team1'] and match_1['team2'] == match_2['team2']) or \
                    (match_1['team1'] == match_2['team2'] and match_1['team2'] == match_2['team1']):

                print(f"Проверяем матч: {match_1['team1']} против {match_1['team2']} с матчем {match_2['team1']} против {match_2['team2']}")

                bet_1_bil = {}
                bet_1_men = {}
                bet_2_bil = {}
                bet_2_men = {}

                for bet in match_1['totals']:
                    if bet['type'] == "більше":
                        bet_1_bil[float(bet['market'])] = float(bet['odds'])
                    elif bet['type'] == "менше":
                        bet_1_men[float(bet['market'])] = float(bet['odds'])

                for bet in match_2['totals']:
                    if bet['type'] == "більше":
                        bet_2_bil[float(bet['market'])] = float(bet['odds'])
                    elif bet['type'] == "менше":
                        bet_2_men[float(bet['market'])] = float(bet['odds'])

                all_totals = set(bet_1_bil.keys()) | set(bet_1_men.keys()) | set(bet_2_bil.keys()) | set(bet_2_men.keys())

                for total_type in all_totals:
                    bet_1_bil_value = bet_1_bil.get(total_type)
                    bet_1_men_value = bet_1_men.get(total_type)
                    bet_2_bil_value = bet_2_bil.get(total_type)
                    bet_2_men_value = bet_2_men.get(total_type)

                    if bet_1_bil_value and bet_2_men_value:
                        stake_1, stake_2 = calculate_arbitrage_bet(bet_1_bil_value, bet_2_men_value, total_bank)
                        if stake_1 and stake_2:
                            win_1 = calculate_win(stake_1, bet_1_bil_value)
                            win_2 = calculate_win(stake_2, bet_2_men_value)

                            total_win = round(win_1 + win_2, 2)
                            if total_win > total_bank:
                                results.append((total_win, "Матч: {} против {}: менше {}, більше {}".format(match_1['team1'], match_1['team2'], bet_1_men_value, bet_2_bil_value)))

                    if bet_1_men_value and bet_2_bil_value:
                        stake_1, stake_2 = calculate_arbitrage_bet(bet_1_men_value, bet_2_bil_value, total_bank)
                        if stake_1 and stake_2:
                            win_1 = calculate_win(stake_1, bet_1_men_value)
                            win_2 = calculate_win(stake_2, bet_2_bil_value)

                            total_win = round(win_1 + win_2, 2)
                            if total_win > total_bank:
                                results.append((total_win, "Матч: {} против {}: менше {}, більше {}".format(match_1['team1'], match_1['team2'], bet_1_men_value, bet_2_bil_value)))
            else:
                print(f"Матч {match_1['team1']} против {match_1['team2']} не найден в другом файле.")

    if results:
        print("Рекомендуем ставить на следующие матчевые ставки с выигрышем больше банка:")
        for result in results:
            print(f"{result[1]} — Выигрыш: {result[0]}")
    else:
        print("Не найдено выгодных ставок.")

filename_1 = 'matches_fav_bet_chempliga.json'
filename_2 = 'matches_v_bet.json'
total_bank = 1000

matches_data_1 = load_matches_from_file(filename_1)
matches_data_2 = load_matches_from_file(filename_2)

if compare_bets_and_calculate(matches_data_1['matches'], matches_data_2['matches'], total_bank):
    print("Рекомендуем ставить!")
else:
    print("Не найдено выгодных ставок.")

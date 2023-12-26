import csv
import random
import pandas as pd
import openpyxl as op
from tabulate import tabulate
import xlsxwriter
from prettytable import PrettyTable

def get_team_names(csv_file):
    team_names = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            team = row['Team Name']
            if team not in team_names:
                team_names.append(team)

    return team_names

def get_ordered_teams_from_excel(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Assuming the teams are sorted by their rank in the Excel file.
    # If not, sort them here. Replace 'Rank' with the actual rank column name if different.
    # df.sort_values(by='Rank', inplace=True)

    team_names = df['Team Name'].tolist()

    # Order the teams as per specified sequence
    ordered_teams = [
        team_names[0],   # Rank 1
        team_names[15],  # Rank 16
        team_names[7],   # Rank 8
        team_names[8],   # Rank 9
        team_names[3],   # Rank 4
        team_names[12],  # Rank 13
        team_names[4],   # Rank 5
        team_names[11],  # Rank 12
        team_names[1],   # Rank 2
        team_names[14],  # Rank 15
        team_names[6],   # Rank 7
        team_names[10],  # Rank 10
        team_names[2],   # Rank 3
        team_names[13],  # Rank 14
        team_names[5],   # Rank 6
        team_names[9]    # Rank 10
    ]
    return ordered_teams

def set_matchups(teams_list):
    all_matchups = []
    matchup = []
    for team in teams_list:
        matchup.append(team)
        if len(matchup) == 2:
            all_matchups.append(matchup)
            matchup = []
    return all_matchups

def read_team_data(csv_file):
    team_stats = {}
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            team = row['Team Name']
            if team not in team_stats:
                team_stats[team] = {
                    'Goals': 0,
                    'Assists': 0,
                    'Saves': 0,
                    'Shots': 0,
                    'Uncertainty': 0,
                    'Players': 0
                }

            # Aggregate stats for each team
            team_stats[team]['Goals'] += float(row['Goals Per Game'])
            team_stats[team]['Assists'] += float(row['Assists Per Game'])
            team_stats[team]['Saves'] += float(row['Saves Per Game'])
            team_stats[team]['Shots'] += float(row['Shots Per Game'])
            team_stats[team]['Uncertainty'] += float(row['Uncertainty Factor'])
            team_stats[team]['Players'] += 1

            # Increase Uncertainty for teams from the 'ME' region
            if 'Region' in row and row['Region'] == 'ME':
                team_stats[team]['Uncertainty'] += 0.015

            if 'Region' in row and row['Region'] == 'SAM':
                team_stats[team]['Uncertainty'] += 0.015

    # Calculate average stats for each team
    for team in team_stats:
        # print(f"Stats for \033[1m{team}\033[0m:")
        for stat in ['Goals', 'Assists', 'Saves', 'Shots', 'Uncertainty']:
            if team_stats[team]['Players'] > 0:  # Check to avoid division by zero
                team_stats[team][stat] /= team_stats[team]['Players']
               #  print(f"\t{stat}: {team_stats[team][stat]:.3f}")  # Formatting numbers to three decimal places
            else:
                print(f"  No players found for {team}, unable to calculate averages.")
        # print("-" * 30)

    return team_stats

def calculate_composite_score(team_stats):
    # Adjust these weights according to how much you value each stat
    weights = {
        'Goals': 0.1,
        'Assists': 0.075,
        'Saves': 0.05,
        'Shots': 0.01,
        'Uncertainty': -0.6  # Negative weight if higher uncertainty is worse
    }

    composite_scores = []
    for team, stats in team_stats.items():
        goals_per_shot = ((stats['Goals'] * weights['Goals']) / (stats['Shots'] * weights['Shots']))
        score = goals_per_shot + (stats['Assists'] * weights['Assists']) + (stats['Saves'] * weights['Saves'])
        final_score = abs(score / (stats['Uncertainty'] * weights['Uncertainty']))
        composite_scores.append(final_score)

    return composite_scores

def write_rankings_to_csv(composite_scores, team_names):
    # Create a DataFrame from the composite scores and team names
    df = pd.DataFrame({
        'Team Name': team_names,
        'Composite Score': composite_scores
    })

    # Sort the DataFrame by composite score
    df.sort_values(by='Composite Score', ascending=False, inplace=True)

    # Use tabulate to print the DataFrame
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False, floatfmt=".3f"))

def simulate_game(team1, team2, team_stats):
    # Base score calculation
    base_score_team1 = (team_stats[team1]['Goals'] / team_stats[team1]['Shots']) + team_stats[team1]['Assists'] * 0.05 - team_stats[team2]['Saves'] * 0.05
    base_score_team2 = (team_stats[team2]['Goals'] / team_stats[team2]['Shots']) + team_stats[team2]['Assists'] * 0.05 - team_stats[team1]['Saves'] * 0.05

    # Random variation based on Uncertainty
    variation_team1 = random.uniform(team_stats[team1]['Uncertainty']*0.15, team_stats[team1]['Uncertainty']*0.85)
    variation_team2 = random.uniform(team_stats[team2]['Uncertainty']*0.15, team_stats[team2]['Uncertainty']*0.85)

    # Final score calculation with reduced random variation and minimum threshold
    team1_score = random.uniform(0, 100*(base_score_team1 - variation_team1))
    team2_score = random.uniform(0, 100*(base_score_team2 - variation_team2))

    # # Print results
    # if team1_score > team2_score:
    #     print(f" \033[1m{team1_score:.3f}\033[0m - {team2_score:.3f}")
    # elif team2_score > team1_score:
    #     print(f" {team1_score:.3f} - \033[1m{team2_score:.3f}\033[0m")

    return team1_score, team2_score

def simulate_series(team1, team2, team_stats):
    team1_game_win, team2_game_win = 0, 0

    for _ in range(1, 8):
        team1_score, team2_score = simulate_game(team1, team2, team_stats)

        if team1_score > team2_score:
            team1_game_win += 1
        elif team2_score > team1_score:
            team2_game_win += 1

        if team1_game_win == 4:
            return 1, 0, team1_game_win, team2_game_win, team1, team2  # Team 1 wins this series
        elif team2_game_win == 4:
            return 0, 1, team1_game_win, team2_game_win, team2, team1  # Team 2 wins this series

def simulate_series_multiple_times(team1, team2, team_stats):
    num_iterations = int(input("Number of Iterations: "))

    total_team1_series_win, total_team2_series_win = 0, 0
    total_team1_game_wins, total_team2_game_wins = 0, 0

    max_length = max(len(team1), len(team2)) + 3  # Maximum length considering the team name and score

    for j in range(1, num_iterations + 1):
        team1_series_win, team2_series_win, team1_game_wins, team2_game_wins, _, _ = simulate_series(team1, team2, team_stats)

        total_team1_series_win += team1_series_win
        total_team2_series_win += team2_series_win
        total_team1_game_wins += team1_game_wins
        total_team2_game_wins += team2_game_wins

        team1_text = f"{team1} {team1_game_wins}"
        team2_text = f"{team2_game_wins} {team2}"
        padding_left = max_length - len(team1_text)
        padding_right = max_length - len(team2_text)

        if team1_series_win == 1:
            print(f"Series {j}: {team1_text} {' ' * padding_left}-{' ' * padding_right} {team2_text}")
        elif team2_series_win == 1:
            print(f"Series {j}: {team1_text} {' ' * padding_left}-{' ' * padding_right} {team2_text}")

    print("*" * 50)
    print(f"{team1} {total_team1_series_win} ({total_team1_game_wins})")
    print(f"{team2} {total_team2_series_win} ({total_team2_game_wins})")

def simulate_single_elim_tournament(teams, team_stats):
    round_num = 1

    # Remaining teams
    remaining_teams = teams

    while len(remaining_teams) > 2:
        # Set matchups for current round
        all_matchups = set_matchups(remaining_teams)
        print(f"\nRound {round_num} matchups:\n")
        for matchup in all_matchups:
            team1, team2 = matchup
            # print(f"\033[1m\033[96m{team1}\033[0m vs \033[1m\033[93m{team2}\033[0m")
            _, _, team1_game_win, team2_game_win, winner, loser = simulate_series(team1, team2, team_stats)

            if team1_game_win == 4:
                print(f"\033[1m\033[96m{winner}\033[0m \033[1m{team1_game_win}\033[0m - {team2_game_win} {loser}")
                # print(f"Winner: \033[1m\033[96m {winner}\033[0m")
            elif team2_game_win == 4:
                print(f"{loser} {team1_game_win} - \033[1m{team2_game_win} \033[93m{winner}\033[0m")
                # print(f"Winner: \033[1m\033[93m {winner}\033[0m")

            # Remove loser and winner from remaining teams list
            remaining_teams.remove(loser)
            remaining_teams.remove(winner)

            # Add winner back to remaining teams list but at the end of the list
            remaining_teams.append(winner)

            # print("- " * 30)
        print("-=" * 40)
        round_num += 1

    # Set Grand Finals matchup
    team1, team2 = remaining_teams[0], remaining_teams[1]
    print(f"\nGrand Finals matchup:")
    # print(f"\033[1m\033[96m{team1}\033[0m vs \033[1m\033[93m{team2}\033[0m")
    # print("- " * 30)
    _, _, team1_game_win, team2_game_win, winner, loser = simulate_series(team1, team2, team_stats)

    if team1_game_win == 4:
        print(f"\033[1m\033[96m{winner}\033[0m \033[1m{team1_game_win}\033[0m - {team2_game_win} {loser}")
        print(f"Winner: \033[1m\033[96m {winner}\033[0m")
    elif team2_game_win == 4:
        print(f"{loser} {team1_game_win} - \033[1m{team2_game_win} \033[93m{winner}\033[0m")
        print(f"Winner: \033[1m\033[93m {winner}\033[0m")

def simulate_double_elim_tournament(teams, team_stats):
    upper_bracket_round_num = 1
    lower_bracket_round_num = 1

    upper_bracket_teams = teams.copy()
    remaining_teams = teams.copy()
    lower_bracket_team_round1 = []
    lower_bracket_team_round2 = []
    lower_bracket_team_round3 = []
    lower_bracket_team_round4 = []
    lower_bracket_team_round5 = []
    lower_bracket_team_final = []

    # Upper Bracket
    while len(remaining_teams) > 2:
        all_matchups_winner = set_matchups(upper_bracket_teams)

        # if upper_bracket_round_num <= 4:
        #     print(f"\nUpper Bracket Round {upper_bracket_round_num} matchups:")

        for matchup in all_matchups_winner:
            team1, team2 = matchup
            # print(f"\033[1m\033[96m{team1}\033[0m vs \033[1m\033[93m{team2}\033[0m")
            _, _, team1_game_win, team2_game_win, winner, loser = simulate_series(team1, team2, team_stats)

            # if team1_game_win == 4:
            #     print(f"\033[1m\033[96m{winner}\033[0m \033[1m{team1_game_win}\033[0m - {team2_game_win} {loser}")
            # elif team2_game_win == 4:
            #     print(f"{loser} {team1_game_win} - \033[1m{team2_game_win} \033[93m{winner}\033[0m")

            if upper_bracket_round_num == 1:
                upper_bracket_teams.remove(loser)
                lower_bracket_team_round1.append(loser)
            elif upper_bracket_round_num == 2:
                upper_bracket_teams.remove(loser)
                lower_bracket_team_round2.append(loser)
            elif upper_bracket_round_num == 3:
                upper_bracket_teams.remove(loser)
                lower_bracket_team_round4.append(loser)
            elif upper_bracket_round_num == 4:
                upper_bracket_teams.remove(loser)
                lower_bracket_team_final.append(loser)

        if upper_bracket_round_num <= 4:
            # print("- " * 30)
            upper_bracket_round_num += 1

        # Loser Bracket
        if lower_bracket_round_num == 1:
            all_matchups_lower = set_matchups(lower_bracket_team_round1)
        elif lower_bracket_round_num == 2:
            all_matchups_lower = set_matchups(lower_bracket_team_round2)
        elif lower_bracket_round_num == 3:
            all_matchups_lower = set_matchups(lower_bracket_team_round3)
        elif lower_bracket_round_num == 4:
            all_matchups_lower = set_matchups(lower_bracket_team_round4)
        elif lower_bracket_round_num == 5:
            all_matchups_lower = set_matchups(lower_bracket_team_round5)
        elif lower_bracket_round_num == 6:
            all_matchups_lower = set_matchups(lower_bracket_team_final)

        # print(f"\nLower Bracket Round {lower_bracket_round_num} matchups:")

        for matchup in all_matchups_lower:
            team1, team2 = matchup
            # print(f"\033[1m\033[96m{team1}\033[0m vs \033[1m\033[93m{team2}\033[0m")
            _, _, team1_game_win, team2_game_win, winner, loser = simulate_series(team1, team2, team_stats)

            # if team1_game_win == 4:
            #     print(f"\033[1m\033[96m{winner}\033[0m \033[1m{team1_game_win}\033[0m - {team2_game_win} {loser}")
            # elif team2_game_win == 4:
            #     print(f"{loser} {team1_game_win} - \033[1m{team2_game_win} \033[93m{winner}\033[0m")

            if lower_bracket_round_num == 1:
                lower_bracket_team_round1.remove(loser)
                lower_bracket_team_round2.append(winner)
                lower_bracket_team_round1.remove(winner)
                remaining_teams.remove(loser)
            elif lower_bracket_round_num == 2:
                lower_bracket_team_round2.remove(loser)
                lower_bracket_team_round3.append(winner)
                lower_bracket_team_round2.remove(winner)
                remaining_teams.remove(loser)
            elif lower_bracket_round_num == 3:
                lower_bracket_team_round3.remove(loser)
                lower_bracket_team_round4.append(winner)
                lower_bracket_team_round3.remove(winner)
                remaining_teams.remove(loser)
            elif lower_bracket_round_num == 4:
                lower_bracket_team_round4.remove(loser)
                lower_bracket_team_round5.append(winner)
                lower_bracket_team_round4.remove(winner)
                remaining_teams.remove(loser)
            elif lower_bracket_round_num == 5:
                lower_bracket_team_round5.remove(loser)
                lower_bracket_team_final.append(winner)
                lower_bracket_team_round5.remove(winner)
                remaining_teams.remove(loser)
            elif lower_bracket_round_num == 6:
                lower_bracket_team_final.remove(loser)
                remaining_teams.remove(loser)

        if lower_bracket_round_num == 1:
            random.shuffle(lower_bracket_team_round2)
        elif lower_bracket_round_num == 2:
            random.shuffle(lower_bracket_team_round3)
        elif lower_bracket_round_num == 3:
            random.shuffle(lower_bracket_team_round4)

        # print("*" * 50)
        lower_bracket_round_num += 1

        if lower_bracket_round_num == 7:
                break

    # Grand Finals
    # print(f"\nGrand Finals:")
    team1 = upper_bracket_teams[0]
    # print(lower_bracket_team_final)
    team2 = lower_bracket_team_final[0]
    # print(f"\033[1m\033[96m{team1}\033[0m vs \033[1m\033[93m{team2}\033[0m")
    _, _, team1_game_win, team2_game_win, winner, loser = simulate_series(team1, team2, team_stats)
    # print(f"\033[1m\033[96m{team1}\033[0m {team1_game_win} - \033[1m{team2_game_win} \033[93m{team2}\033[0m")
    # # print(f"Grand Champ: \033[1m {winner}\033[0m")
    # print("\/" * 100)

    return winner

def simulate_double_elim_tournament_multiple_times(teams, team_stats):
    num_iterations = int(input("Number of Iterations: "))
    tournaments_done = 0
    total_wins = {teams: 0 for teams in teams}

    for _ in range(num_iterations):
        winner = simulate_double_elim_tournament(teams, team_stats)
        total_wins[winner] += 1
        tournaments_done += 1
        print(f"\rTournaments Done: {tournaments_done}/{num_iterations}", end="")
    print()

    win_percentages = {team: (wins / num_iterations) * 100 for team, wins in total_wins.items()}

    # Sort the win percentages in descending order
    sorted_win_percentages = sorted(win_percentages.items(), key=lambda x: x[1], reverse=True)

    print("\nWin Percentages: ")
    for team, win_percentage in sorted_win_percentages:
        tourney_wins = total_wins[team]
        print(f"{team}: {win_percentage:.2f}% ({tourney_wins} wins)")


def main():
    # Read team data from CSV file
    csv_file = 'C:/Users/maxim/PycharmProjects/RLCS_Simulation/RLCSsheet.csv'
    team_stats = read_team_data(csv_file)

    # Get user selection
    selection = input("(1) Simulate a BO7 series\n"
                                 "(2) Rank all teams\n"
                                 "(3) Simulate 16-team SINGLE elimination tournament\n"
                                 "(4) Simulate 16-team DOUBLE elimination tournament\n\n"
                                 "Selection: ")

    if selection == '1':
        # Get team names from user
        team1 = input("Team 1: ")
        team2 = input("Team 2: ")

        # Simulate a Best of 7 series
        simulate_series_multiple_times(team1, team2, team_stats)


    elif selection == '2':
        composite_scores = calculate_composite_score(team_stats)
        team_names = get_team_names(csv_file)

        # Write the rankings to an Excel file
        write_rankings_to_csv(composite_scores, team_names)


    elif selection == '3':
        teams = []
        for i in range(1, 17):
            team_name = input(f"Team {i}: ")
            teams.append(team_name)
            i += 1

        # Simulate a 16-team single elimination tournament
        simulate_single_elim_tournament(teams, team_stats)


    elif selection == '4':
        file_path = 'C:/Users/maxim/PycharmProjects/RLCS_Simulation/rankings.xlsx'
        ordered_teams = get_ordered_teams_from_excel(file_path)
        print(ordered_teams)

        # Simulate a 16-team double elimination tournament
        simulate_double_elim_tournament_multiple_times(ordered_teams, team_stats)

if __name__ == "__main__":
    main()

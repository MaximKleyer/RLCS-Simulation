import csv
import random
import pandas as pd
import openpyxl as op

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
                team_stats[team]['Uncertainty'] += 0.01

            if 'Region' in row and row['Region'] == 'SAM':
                team_stats[team]['Uncertainty'] += 0.0125

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
        'Goals': 0.20,
        'Assists': 0.15,
        'Saves': 0.135,
        'Shots': 0.025,
        'Uncertainty': -0.45  # Negative weight if higher uncertainty is worse
    }

    composite_scores = {}
    for team, stats in team_stats.items():
        goals_per_shot = ((stats['Goals'] * weights['Goals']) /(stats['Shots'] * weights['Shots']))
        score = goals_per_shot + (stats['Assists'] * weights['Assists']) + (stats['Saves'] * weights['Saves'])
        composite_scores[team] = abs(score / (stats['Uncertainty'] * weights['Uncertainty']))

    return composite_scores

def write_rankings_to_excel(team_names, scores, filename):
    # Create a DataFrame using team names and scores as separate columns
    df = pd.DataFrame({
        'Team Name': team_names,
        'Score': scores
    })

    # Sort the DataFrame by 'Score' in descending order
    df.sort_values(by='Score', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1  # Adjusting index to start from 1 for ranking
    df.index.name = 'Rank'  # Naming the index column as 'Rank'

    # Write DataFrame to an Excel file
    df.to_excel(filename, index=True)

def read_and_sort_excel(filename):
    # Read Excel file
    df = pd.read_excel(filename, index_col='Rank')

    # Sort the DataFrame by 'Rank'
    df.sort_index(inplace=True)

    # Determine the maximum width needed for the 'Team Name' column, adding extra space
    max_team_name_width = max(df['Team Name'].apply(len).max(), len('Team Name')) + 5  # Added 5 extra spaces

    # Determine the width for the 'Score' column (assuming a maximum of 2 decimal places)
    score_width = max(df['Score'].apply(lambda x: f"{x:.2f}").apply(len).max(), len('Score'))

    # Print header with proper alignment
    print(f"{'Rank':<5} {'Team Name':<{max_team_name_width}} {'Score':>{score_width}}")

    # Print each row with formatted columns
    for rank, row in df.iterrows():
        print(f"{rank:<10} {row['Team Name']:<{max_team_name_width}} {row['Score']:>{score_width}.2f}")

def simulate_game(team1, team2, team_stats):
    # Base score calculation
    base_score_team1 = (team_stats[team1]['Goals'] / team_stats[team1]['Shots']) + team_stats[team1]['Assists'] * 0.05 - team_stats[team2]['Saves'] * 0.05
    base_score_team2 = (team_stats[team2]['Goals'] / team_stats[team2]['Shots']) + team_stats[team2]['Assists'] * 0.05 - team_stats[team1]['Saves'] * 0.05

    # Random variation based on Uncertainty
    variation_team1 = random.uniform(team_stats[team1]['Uncertainty']*0.3, team_stats[team1]['Uncertainty']*0.85)
    variation_team2 = random.uniform(team_stats[team2]['Uncertainty']*0.3, team_stats[team2]['Uncertainty']*0.85)

    # Final score calculation with reduced random variation and minimum threshold
    team1_score = random.uniform(0, 100*(base_score_team1 - variation_team1))
    team2_score = random.uniform(0, 100*(base_score_team2 - variation_team2))

    # Print results
    if team1_score > team2_score:
        print(f" \033[1m{team1_score:.3f}\033[0m - {team2_score:.3f}")
    elif team2_score > team1_score:
        print(f" {team1_score:.3f} - \033[1m{team2_score:.3f}\033[0m")

    return team1_score, team2_score

def simulate_series(team1, team2, team_stats):
    team1_game_win, team2_game_win = 0, 0
    team1_series_win, team2_series_win = 0, 0
    total_team1_game_wins, total_team2_game_wins = 0, 0

    for i in range(1, 8):
        team1_score, team2_score = simulate_game(team1, team2, team_stats)

        if team1_score > team2_score:
            team1_game_win += 1
            total_team1_game_wins += 1
        elif team2_score > team1_score:
            team2_game_win += 1
            total_team2_game_wins += 1

        if team1_game_win == 4:
            # print(f"\nSeries {j}\n\033[1m\033[96m{team1} \033[0m{team1_game_win} - {team2_game_win} \033[93m{team2}\033[0m")
            team1_series_win += 1
            team1_game_win = 0
            team2_game_win = 0
            break
        elif team2_game_win == 4:
            # print(f"\nSeries {j} \n\033[96m{team1} \033[0m{team1_game_win} - {team2_game_win} \033[1m\033[93m{team2}\033[0m")
            team2_series_win += 1
            team1_game_win = 0
            team2_game_win = 0
            break
        i += 1

    if team1_series_win > team2_series_win:
        winner_team = team1
        loser_team = team2
        winner_series_wins = team1_series_win
        loser_series_wins = team2_series_win
    elif team2_series_win > team1_series_win:
        winner_team = team2
        loser_team = team1
        winner_series_wins = team2_series_win
        loser_series_wins = team1_series_win
    else:
        print("Womp")

    return winner_team, loser_team, winner_series_wins, loser_series_wins

def simulate_single_elim_tournament(teams, team_stats):
    round_num = 1

    def set_matchups(teams_list):
        all_matchups = []
        matchup = []
        for team in teams_list:
            matchup.append(team)
            if len(matchup) == 2:
                all_matchups.append(matchup)
                matchup = []
        return all_matchups

    # Remaining teams
    remaining_teams = teams

    while len(remaining_teams) > 2:
        # Set matchups for current round
        all_matchups = set_matchups(remaining_teams)
        print(f"\nRound {round_num} matchups:")
        for matchup in all_matchups:
            team1, team2 = matchup
            print(f"\033[1m\033[96m{team1}\033[0m vs \033[1m\033[93m{team2}\033[0m")
            print("- " * 30)
            winner_team, loser_team, winner_series_wins, loser_series_wins = simulate_series(team1, team2, team_stats)
            remaining_teams.remove(loser_team)
            print("=-" * 40)
        round_num += 1

    # Set Grand Finals matchup
    team1, team2 = remaining_teams[0], remaining_teams[1]
    print(f"\nGrand Finals matchup:")
    print(f"\033[1m\033[96m{team1}\033[0m vs \033[1m\033[93m{team2}\033[0m")
    print("- " * 30)
    winner_team, loser_team, winner_series_wins, loser_series_wins = simulate_series(team1, team2, team_stats)
    print(f"Winner: \033[1m\033[96m {winner_team}\033[0m")

def main():
    # Read team data from CSV file
    csv_file = 'C:/Users/nycdoe/PycharmProjects/RLCS_Simulation/RLCSsheet.csv'
    team_stats = read_team_data(csv_file)

    # Get user selection
    selection = input("(1) Simulate a BO7 series\n(2) Rank all teams\n(3) Simulate 16-team single elimination tournament\n\nSelection: ")

    if selection == '1':
        # Get team names from user
        team1 = input("Team 1: ")
        team2 = input("Team 2: ")

        # Simulate a Best of 7 series
        simulate_series(team1, team2, team_stats)


    elif selection == '2':
        composite_scores = calculate_composite_score(team_stats)

        # Extract team names and scores separately from composite_scores
        team_names = list(composite_scores.keys())
        scores = list(composite_scores.values())

        # Write the rankings to an Excel file
        write_rankings_to_excel(team_names, scores, 'rankings.xlsx')

        # Read and display the sorted Excel file
        read_and_sort_excel('rankings.xlsx')


    elif selection == '3':
        teams = []
        for i in range(1, 5):
            team_name = input(f"Team {i}: ")
            teams.append(team_name)
            i += 1

        # Simulate a 16-team single elimination tournament
        simulate_single_elim_tournament(teams, team_stats)

if __name__ == "__main__":
    main()

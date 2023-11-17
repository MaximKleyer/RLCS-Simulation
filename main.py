import csv
import random

# Player class
class Player:
    def __init__(self, name, goals_per_game, assists_per_game, saves_per_game, shots_per_game, uncertainty, team_name):
        self.name = name
        self.goals_per_game = float(goals_per_game)
        self.assists_per_game = float(assists_per_game)
        self.saves_per_game = float(saves_per_game)
        self.shots_per_game = float(shots_per_game)
        self.shooting_percentage = self.goals_per_game / self.shots_per_game
        self.uncertainty = float(uncertainty)
        self.team_name = team_name

    def calculate_rating(self):
        return (self.goals_per_game + self.assists_per_game + self.saves_per_game) / 3 * self.shots_per_game

    def play_game(self, team1, team2, overtime=False):
        goals_scored = 0
        assists_made = 0
        saves_made = 0
        shots_taken = 0

        # Adjust the number of iterations for regular or overtime
        num_iterations = 2 if not overtime else 1

        for _ in range(num_iterations):
            # Calculate scoring chance based on the saves per game of both teams
            team1_saves_per_game = sum(player.saves_per_game for player in team1.players)
            team2_saves_per_game = sum(player.saves_per_game for player in team2.players)
            # Calculate scoring chance based on the assists per game of both teams
            team1_assists_per_game = sum(player.assists_per_game for player in team1.players)
            team2_assists_per_game = sum(player.assists_per_game for player in team2.players)

            if self.team_name == team1.name:
                scoring_chance = (self.shooting_percentage + self.shots_per_game * .04 + self.goals_per_game * .04 + ((team1_assists_per_game / 9) * .05)) - (self.uncertainty * .4)  - ((team2_saves_per_game / 9) * .05)
            elif self.team_name == team2.name:
                scoring_chance = (self.shooting_percentage + self.shots_per_game * .04 + self.goals_per_game * .04 + ((team2_assists_per_game / 9) * .05)) - (self.uncertainty * .4)  - ((team1_saves_per_game / 9) * .05)
            else:
                raise ValueError("Player's team is not one of the provided teams.")

            if random.random() < scoring_chance:
                goals_scored += 1
            # Simulate assists and saves (adjust as needed)
            if random.random() < self.assists_per_game:
                assists_made += 1
            if random.random() < self.saves_per_game:
                saves_made += 1
            # Track total shots taken
            shots_taken += 1

        return {
            'player': self.name,
            'team': self.team_name,
            'goals_scored': goals_scored,
            'assists_made': assists_made,
            'saves_made': saves_made,
            'shots_taken': shots_taken
        }

# Team class
class Team:
    def __init__(self, name, players):
        self.name = name
        self.players = players

    def play_game(self, other_team, overtime=False):
        self_scores = []
        other_scores = []

        for player in self.players:
            self_scores.append(player.play_game(self, other_team, overtime))  # Pass both teams to play_game

        for player in other_team.players:
            other_scores.append(player.play_game(other_team, self, overtime))  # Pass both teams to play_game

        return self_scores, other_scores

def simulate_series(team1, team2):
    team1_wins = 0
    team2_wins = 0

    for game_num in range(1, 8):  # Allow for potential overtime
        # Ensure other_team is always an instance of Team
        team1_players = team1.players
        team2_players = team2.players

        # Create teams
        team1_instance = Team(team1.name, team1_players)
        team2_instance = Team(team2.name, team2_players)

        self_scores, other_scores = team1_instance.play_game(team2_instance)

        # Calculate team scores
        self_score = sum(score['goals_scored'] for score in self_scores)
        other_score = sum(score['goals_scored'] for score in other_scores)

        # Determine the winner of the game
        if self_score > other_score:
            team1_wins += 1
            print(f"Game {game_num}: \033[1m\033[96m{team1.name}\033[0m {self_score} : {other_score} {team2.name}")
        elif other_score > self_score:
            team2_wins += 1
            print(f"Game {game_num}: {team1.name} {self_score} : {other_score} \033[1m\033[93m{team2.name}\033[0m")
        else:
            # Simulate overtime - one goal sudden death
            while True:
                self_ot_score, other_ot_score = team1_instance.play_game(team2_instance, overtime=True)

                # Check if there is a winner after the overtime
                if self_ot_score[0]['goals_scored'] != other_ot_score[0]['goals_scored']:
                    break

            # Determine the winner of the overtime
            if self_ot_score[0]['goals_scored'] > other_ot_score[0]['goals_scored']:
                team1_wins += 1
                print(f"Game {game_num}: \033[1m\033[96m{team1.name}\033[0m {self_score + 1} : {other_score} {team2.name} (OT)")
            elif self_ot_score[0]['goals_scored'] < other_ot_score[0]['goals_scored']:
                team2_wins += 1
                print(f"Game {game_num}: {team1.name} {self_score} : {other_score + 1} \033[1m\033[93m{team2.name}\033[0m (OT)")

        if team1_wins == 4 or team2_wins == 4:
            break

    if team1_wins > team2_wins:
        print(f"\n\033[1m\033[96m{team1.name}\033[0m wins the series {team1_wins}-{team2_wins}!")
        return team1, team1_wins, team2_wins
    else:
        print(f"\n\033[1m\033[93m{team2.name}\033[0m wins the series {team2_wins}-{team1_wins}!")
        return team2, team1_wins, team2_wins

def read_players_from_csv(file_path):
    players = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            player = Player(
                row['Player Name'],
                row['Goals Per Game'],
                row['Assists Per Game'],
                row['Saves Per Game'],
                row['Shots Per Game'],
                row['Uncertainty Factor'],
                row['Team Name']
            )
            players.append(player)
    return players

def get_players_by_team(players, team_name):
    return [player for player in players if player.team_name == team_name]

# Simulate the series multiple times
def simulate_series_multiple_times(team1, team2, num_simulations):
    team1_total_wins = 0
    team2_total_wins = 0

    for _ in range(num_simulations):
        # Ensure other_team is always an instance of Team
        team1_players = team1.players
        team2_players = team2.players

        # Create teams
        team1_instance = Team(team1.name, team1_players)
        team2_instance = Team(team2.name, team2_players)

        team1_wins, team2_wins = simulate_series(team1_instance, team2_instance)

        # Update total wins for each team
        if team1_wins > team2_wins:
            team1_total_wins += 1
        else:
            team2_total_wins += 1

        print('-' * 50)  # Add a separator between simulations

    print(
        f"\nTotal Series Wins:\n\033[1m\033[96m{team1.name}\033[0m: {team1_total_wins}\n\033[1m\033[93m{team2.name}\033[0m: {team2_total_wins}")
    return team1_total_wins, team2_total_wins

def simulate_tournament(teams):
    # Check if the number of teams is a power of 2
    num_teams = len(teams)
    if num_teams < 2 or not num_teams & (num_teams - 1) == 0:
        raise ValueError("The number of teams must be a power of 2.")

    # Simulate rounds until there's only one team left
    round_num = 1
    while len(teams) > 1:
        print(f"\n\033[1mRound {round_num}\033[0m")
        winners = []
        for i in range(0, len(teams), 2):
            team1 = teams[i]
            team2 = teams[i + 1]

            print(f"\nMatchup: \033[1m\033[96m{team1.name}\033[0m vs \033[1m\033[93m{team2.name}\033[0m")
            print("- " * 30)

            # Simulate the series
            series_winner, team1_score, team2_score = simulate_series(team1, team2)

            # Determine the winner of the series
            winners.append(series_winner)

            print("=-" * 40)

        # Move winners to the next round
        teams = winners
        round_num += 1

    # Print the winner of the tournament
    print(f"\n\033[1m\033[92m{teams[0].name}\033[0m wins the tournament!")

def simulate_tournament_multiple_times(teams, num_simulations):
    # Check if the number of teams is a power of 2
    num_teams = len(teams)
    if num_teams < 2 or not num_teams & (num_teams - 1) == 0:
        raise ValueError("The number of teams must be a power of 2.")

    # Initialize counters and dictionaries to track statistics
    round2_counts = {team.name: 0 for team in teams}
    round3_counts = {team.name: 0 for team in teams}
    tournament_wins = {team.name: 0 for team in teams}

    for _ in range(num_simulations):
        # Copy the original list of teams to avoid modifying the original
        current_teams = list(teams)

        # Simulate rounds until there's only one team left
        round_num = 1
        while len(current_teams) > 1:
            print(f"\n\033[1mRound {round_num}\033[0m")
            winners = []
            for i in range(0, len(current_teams), 2):
                team1 = current_teams[i]
                team2 = current_teams[i + 1]

                print(f"\nMatchup: \033[1m\033[96m{team1.name}\033[0m vs \033[1m\033[93m{team2.name}\033[0m")
                print("- " * 30)

                # Unpack the tuple returned by simulate_series
                series_winner, _, _ = simulate_series(team1, team2)

                # Determine the winner of the series
                winners.append(series_winner)

                print("=-" * 40)

            # Move winners to the next round
            current_teams = winners
            round_num += 1

        # Count the teams that made it to each round
        for team in teams:
            if team in current_teams:
                if round_num == 2:
                    round2_counts[team.name] += 1
                elif round_num == 3:
                    round3_counts[team.name] += 1

        # Count tournament wins
        tournament_wins[current_teams[0].name] += 1

    # Calculate percentages
    round2_percentages = {team: (count / num_simulations) * 100 for team, count in round2_counts.items()}
    round3_percentages = {team: (count / num_simulations) * 100 for team, count in round3_counts.items()}
    tournament_win_percentages = {team: (count / num_simulations) * 100 for team, count in tournament_wins.items()}

    # Print the results
    print("\nPercentage of Teams Making it to Round 2:")
    for team, percentage in round2_percentages.items():
        print(f"{team}: {percentage:.2f}%")

    print("\nPercentage of Teams Making it to Round 3:")
    for team, percentage in round3_percentages.items():
        print(f"{team}: {percentage:.2f}%")

    print("\nPercentage of Tournament Wins:")
    for team, percentage in tournament_win_percentages.items():
        print(f"{team}: {percentage:.2f}%")

# Read players from CSV file
players = read_players_from_csv('C:/Users/nycdoe/PycharmProjects/Simulation/Players.csv')

# Get unique team names
team_names = set(player.team_name for player in players)

# Allow the user to choose between a single series or a tournament
simulation_type = input("Enter 'series' for a single series or 'tournament' for a tournament: ")

if simulation_type == "series":
    # Allow user to choose teams
    team1_name = input("Enter Team 1 name: ")
    team2_name = input("Enter Team 2 name: ")

    # Check if the entered team names exist in the dataset
    if team1_name not in team_names or team2_name not in team_names:
        print("Invalid team names. Please enter valid team names.")
    else:
        # Get players based on team name
        team1_players = get_players_by_team(players, team1_name)
        team2_players = get_players_by_team(players, team2_name)

        # Create teams
        team1 = Team(team1_name, team1_players)
        team2 = Team(team2_name, team2_players)

        # Simulate the series
        simulate_series_multiple_times(team1, team2, int(input("Number of Simulations: ")))

elif simulation_type == "tournament":
    # Allow the user to choose 8 teams for the tournament
    tournament_teams = []
    for i in range(8):
        team_name = input(f"Enter Team {i + 1} name: ")
        if team_name not in team_names:
            print(f"Invalid team name '{team_name}'. Please enter a valid team name.")
            break
        else:
            team_players = get_players_by_team(players, team_name)
            team = Team(team_name, team_players)
            tournament_teams.append(team)

    # Allow the user to choose the number of tournament simulations
    num_tournament_simulations = int(input("Enter the number of tournament simulations: "))

    # Simulate the tournament multiple times
    simulate_tournament_multiple_times(tournament_teams, num_tournament_simulations)
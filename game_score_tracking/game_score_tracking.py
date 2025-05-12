# import time
# from functools import wraps
# import mysql.connector
# from colorama import Fore, Style, init
# from tabulate import tabulate
# import matplotlib.pyplot as plt

# init(autoreset=True)

# # Retry Decorator
# def retry(max_retries=3, delay=2):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             for attempt in range(1, max_retries + 1):
#                 try:
#                     return func(*args, **kwargs)
#                 except Exception as e:
#                     print(Fore.YELLOW + f"[Retry {attempt}] Failed due to: {e}")
#                     time.sleep(delay)
#             raise Exception("All retry attempts failed.")
#         return wrapper
#     return decorator

# # Game Score Tracker
# class GameScoreTracker:
#     def __init__(self):
#         self.conn = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="2798",
#             database="games_scores"
#         )
#         self.cursor = self.conn.cursor()

#     def add_player(self, username):
#         self.cursor.execute("INSERT IGNORE INTO players (username) VALUES (%s)", (username,))
#         self.conn.commit()

#     def add_game(self, game_name):
#         self.cursor.execute("INSERT IGNORE INTO games (game_name) VALUES (%s)", (game_name,))
#         self.conn.commit()

#     def get_player_id(self, username):
#         self.cursor.execute("SELECT player_id FROM players WHERE username = %s", (username,))
#         result = self.cursor.fetchone()
#         if result:
#             return result[0]
#         raise Exception(f"Player '{username}' not found.")

#     def get_game_id(self, game_name):
#         self.cursor.execute("SELECT game_id FROM games WHERE game_name = %s", (game_name,))
#         result = self.cursor.fetchone()
#         if result:
#             return result[0]
#         raise Exception(f"Game '{game_name}' not found.")

#     @retry()
#     def submit_score(self, username, game_name, score):
#         self.add_player(username)
#         self.add_game(game_name)
#         player_id = self.get_player_id(username)
#         game_id = self.get_game_id(game_name)

#         self.cursor.execute(
#             "INSERT INTO scores (player_id, game_id, score) VALUES (%s, %s, %s)",
#             (player_id, game_id, score)
#         )
#         self.conn.commit()
#         print(Fore.GREEN + "✅ Score submitted successfully!")

#     def view_leaderboard(self, game_name=None):
#         if game_name:
#             self.cursor.execute(""" 
#                 SELECT p.username, g.game_name, MAX(s.score) AS top_score 
#                 FROM scores s
#                 JOIN players p ON s.player_id = p.player_id
#                 JOIN games g ON s.game_id = g.game_id
#                 WHERE g.game_name = %s
#                 GROUP BY p.username, g.game_name
#                 ORDER BY top_score DESC
#                 LIMIT 10
#             """, (game_name,))
#         else:
#             self.cursor.execute("""
#                 SELECT p.username, g.game_name, SUM(s.score) AS total_score
#                 FROM scores s
#                 JOIN players p ON s.player_id = p.player_id
#                 JOIN games g ON s.game_id = g.game_id
#                 GROUP BY p.username, g.game_name
#                 ORDER BY total_score DESC
#                 LIMIT 10
#             """)

#         rows = self.cursor.fetchall()
#         print(Fore.CYAN + "\n🏆 Leaderboard:")
#         print(tabulate(rows, headers=["Player", "Game", "Score"], tablefmt="fancy_grid"))

#     def generate_statistics(self):
#         print(Fore.MAGENTA + "\n📊 Game Statistics:")

#         # General Statistics
#         self.cursor.execute("SELECT COUNT(*) FROM players")
#         total_players = self.cursor.fetchone()[0]
#         self.cursor.execute("SELECT COUNT(*) FROM games")
#         total_games = self.cursor.fetchone()[0]
#         self.cursor.execute("SELECT COUNT(*) FROM scores")
#         total_scores = self.cursor.fetchone()[0]

#         print(Fore.GREEN + "\n📋 General Stats:")
#         print(Fore.YELLOW + f"Total Players: {total_players}")
#         print(Fore.YELLOW + f"Total Games: {total_games}")
#         print(Fore.YELLOW + f"Total Scores Recorded: {total_scores}")

#         # Game Statistics (Average Score per Game)
#         self.cursor.execute("""
#             SELECT g.game_name, ROUND(AVG(s.score), 2) AS avg_score
#             FROM scores s
#             JOIN games g ON s.game_id = g.game_id
#             GROUP BY g.game_name
#         """)
#         results = self.cursor.fetchall()
#         print(Fore.GREEN + "\n🎮 Game Stats:")
#         for game_name, avg_score in results:
#             print(Fore.YELLOW + f"- {game_name}: Avg Score = {avg_score}")

#         # Chart - Average Score per Game
#         games = [row[0] for row in results]
#         avg_scores = [row[1] for row in results]

#         plt.figure(figsize=(10, 5))
#         plt.bar(games, avg_scores, color='skyblue')
#         plt.title("Average Score per Game")
#         plt.xlabel("Game")
#         plt.ylabel("Average Score")
#         plt.xticks(rotation=45)
#         plt.tight_layout()
#         plt.show()

#         # Best Player (highest score overall)
#         self.cursor.execute("""
#             SELECT p.username, SUM(s.score) AS total_score
#             FROM scores s
#             JOIN players p ON s.player_id = p.player_id
#             GROUP BY p.username
#             ORDER BY total_score DESC
#             LIMIT 1
#         """)
#         best_player = self.cursor.fetchone()
#         print(Fore.GREEN + "\n👑 Best Overall Player:")
#         if best_player:
#             print(Fore.YELLOW + f"{best_player[0]} with Total Score = {best_player[1]}")

#         # Chart - Best Player by Total Score
#         plt.figure(figsize=(6, 4))
#         plt.bar([best_player[0]], [best_player[1]], color='gold')
#         plt.title("Best Overall Player")
#         plt.xlabel("Player")
#         plt.ylabel("Total Score")
#         plt.tight_layout()
#         plt.show()

#         # Best Player for Each Game
#         print(Fore.GREEN + "\n🥇 Best Player Per Game:")
#         self.cursor.execute("SELECT game_id, game_name FROM games")
#         all_games = self.cursor.fetchall()

#         for game_id, game_name in all_games:
#             self.cursor.execute("""
#                 SELECT p.username, MAX(s.score) AS top_score
#                 FROM scores s
#                 JOIN players p ON s.player_id = p.player_id
#                 WHERE s.game_id = %s
#                 GROUP BY p.username
#                 ORDER BY top_score DESC
#                 LIMIT 1
#             """, (game_id,))
#             result = self.cursor.fetchone()
#             if result:
#                 print(Fore.YELLOW + f"- {game_name}: {result[0]} with Score = {result[1]}")

# # CLI Menu
# def menu():
#     tracker = GameScoreTracker()
#     while True:
#         print(Fore.BLUE + "\n📋 MENU")
#         print("1. Submit Score")
#         print("2. View Leaderboard")
#         print("3. View Game Stats")
#         print("4. Exit")

#         choice = input("Enter your choice: ").strip()
#         if choice == "1":
#             username = input("Enter player name: ").strip()
#             game = input("Enter game name: ").strip()
#             try:
#                 score = int(input("Enter score: ").strip())
#                 tracker.submit_score(username, game, score)
#             except ValueError:
#                 print(Fore.RED + "❌ Invalid score! Must be a number.")
#         elif choice == "2":
#             game_filter = input("Enter game name (or press Enter for all games): ").strip()
#             tracker.view_leaderboard(game_filter if game_filter else None)
#         elif choice == "3":
#             tracker.generate_statistics()
#         elif choice == "4":
#             print(Fore.GREEN + "👋 Exiting... Goodbye!")
#             break
#         else:
#             print(Fore.RED + "❌ Invalid choice!")

# if __name__ == "__main__":
#     menu()



import time
from functools import wraps
import mysql.connector
from colorama import Fore, Style, init
from tabulate import tabulate
import matplotlib.pyplot as plt

# Initialize colorama
init(autoreset=True)

# Retry Decorator
def retry(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(Fore.YELLOW + f"[Retry {attempt}] Failed due to: {e}")
                    time.sleep(delay)
            raise Exception("All retry attempts failed.")
        return wrapper
    return decorator

# Game Score Tracker
class GameScoreTracker:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2798",
            database="games_scores"
        )
        self.cursor = self.conn.cursor()

    def add_player(self, username):
        self.cursor.execute("INSERT IGNORE INTO players (username) VALUES (%s)", (username,))
        self.conn.commit()

    def add_game(self, game_name):
        self.cursor.execute("INSERT IGNORE INTO games (game_name) VALUES (%s)", (game_name,))
        self.conn.commit()

    def get_player_id(self, username):
        self.cursor.execute("SELECT player_id FROM players WHERE username = %s", (username,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        raise Exception(f"Player '{username}' not found.")

    def get_game_id(self, game_name):
        self.cursor.execute("SELECT game_id FROM games WHERE game_name = %s", (game_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        raise Exception(f"Game '{game_name}' not found.")

    @retry()
    def submit_score(self, username, game_name, score):
        self.add_player(username)
        self.add_game(game_name)
        player_id = self.get_player_id(username)
        game_id = self.get_game_id(game_name)

        self.cursor.execute(
            "INSERT INTO scores (player_id, game_id, score) VALUES (%s, %s, %s)",
            (player_id, game_id, score)
        )
        self.conn.commit()
        print(Fore.GREEN + "✅ Score submitted successfully!")

    def view_leaderboard(self, game_name=None):
        if game_name:
            self.cursor.execute(""" 
                SELECT p.username, g.game_name, MAX(s.score) AS top_score 
                FROM scores s
                JOIN players p ON s.player_id = p.player_id
                JOIN games g ON s.game_id = g.game_id
                WHERE g.game_name = %s
                GROUP BY p.username, g.game_name
                ORDER BY top_score DESC
                LIMIT 10
            """, (game_name,))
        else:
            self.cursor.execute(""" 
                SELECT p.username, g.game_name, SUM(s.score) AS total_score
                FROM scores s
                JOIN players p ON s.player_id = p.player_id
                JOIN games g ON s.game_id = g.game_id
                GROUP BY p.username, g.game_name
                ORDER BY total_score DESC
                LIMIT 10
            """)

        rows = self.cursor.fetchall()
        print(Fore.CYAN + "\n🏆 Leaderboard:")
        print(tabulate(rows, headers=["Player", "Game", "Score"], tablefmt="fancy_grid"))

    def generate_statistics(self):
        print(Fore.MAGENTA + "\n📊 Game Statistics:")

        # General Statistics
        self.cursor.execute("SELECT COUNT(*) FROM players")
        total_players = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM games")
        total_games = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM scores")
        total_scores = self.cursor.fetchone()[0]

        print(Fore.GREEN + "\n📋 General Stats:")
        print(Fore.YELLOW + f"Total Players: {total_players}")
        print(Fore.YELLOW + f"Total Games: {total_games}")
        print(Fore.YELLOW + f"Total Scores Recorded: {total_scores}")

        # Game Statistics (Average Score per Game)
        self.cursor.execute(""" 
            SELECT g.game_name, ROUND(AVG(s.score), 2) AS avg_score
            FROM scores s
            JOIN games g ON s.game_id = g.game_id
            GROUP BY g.game_name
        """)
        results = self.cursor.fetchall()
        print(Fore.GREEN + "\n🎮 Game Stats:")
        for game_name, avg_score in results:
            print(Fore.YELLOW + f"- {game_name}: Avg Score = {avg_score}")

        # Chart - Average Score per Game
        games = [row[0] for row in results]
        avg_scores = [row[1] for row in results]

        plt.figure(figsize=(10, 5))
        plt.bar(games, avg_scores, color='skyblue')
        plt.title("Average Score per Game")
        plt.xlabel("Game")
        plt.ylabel("Average Score")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Best Player (highest score overall)
        self.cursor.execute(""" 
            SELECT p.username, SUM(s.score) AS total_score
            FROM scores s
            JOIN players p ON s.player_id = p.player_id
            GROUP BY p.username
            ORDER BY total_score DESC
            LIMIT 1
        """)
        best_player = self.cursor.fetchone()
        print(Fore.GREEN + "\n👑 Best Overall Player:")
        if best_player:
            print(Fore.YELLOW + f"{best_player[0]} with Total Score = {best_player[1]}")

        # Chart - Best Player by Total Score
        plt.figure(figsize=(6, 4))
        plt.bar([best_player[0]], [best_player[1]], color='gold')
        plt.title("Best Overall Player")
        plt.xlabel("Player")
        plt.ylabel("Total Score")
        plt.tight_layout()
        plt.show()

        # Best Player for Each Game
        print(Fore.GREEN + "\n🥇 Best Player Per Game:")
        self.cursor.execute("SELECT game_id, game_name FROM games")
        all_games = self.cursor.fetchall()

        for game_id, game_name in all_games:
            self.cursor.execute(""" 
                SELECT p.username, MAX(s.score) AS top_score
                FROM scores s
                JOIN players p ON s.player_id = p.player_id
                WHERE s.game_id = %s
                GROUP BY p.username
                ORDER BY top_score DESC
                LIMIT 1
            """, (game_id,))
            result = self.cursor.fetchone()
            if result:
                print(Fore.YELLOW + f"- {game_name}: {result[0]} with Score = {result[1]}")

# CLI Menu
def menu():
    tracker = GameScoreTracker()
    while True:
        print(Fore.BLUE + "\n📋 MENU")
        print("1. Submit Score")
        print("2. View Leaderboard")
        print("3. View Game Stats")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            username = input("Enter player name: ").strip()
            # Player name validation: should not contain numbers
            if any(char.isdigit() for char in username):
                print(Fore.RED + "❌ Player name cannot contain numbers.")
                continue
            
            game = input("Enter game name: ").strip()
            # Game name validation: should not contain numbers
            if any(char.isdigit() for char in game):
                print(Fore.RED + "❌ Game name cannot contain numbers.")
                continue

            try:
                score = int(input("Enter score: ").strip())
            except ValueError:
                print(Fore.RED + "❌ Invalid score! Must be a number.")
                continue
            tracker.submit_score(username, game, score)
            
        elif choice == "2":
            game_filter = input("Enter game name (or press Enter for all games): ").strip()
            # Game name validation: should not contain numbers
            if game_filter and any(char.isdigit() for char in game_filter):
                print(Fore.RED + "❌ Game name cannot contain numbers.")
                continue
            tracker.view_leaderboard(game_filter if game_filter else None)

        elif choice == "3":
            tracker.generate_statistics()
        elif choice == "4":
            print(Fore.GREEN + "👋 Exiting... Goodbye!")
            break
        else:
            print(Fore.RED + "❌ Invalid choice!")

if __name__ == "__main__":
    menu()

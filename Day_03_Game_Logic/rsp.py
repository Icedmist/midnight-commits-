# simple rock, paper scissors game
import random

def get_computer_choice():
    return random.choice(['rock', 'paper', 'scissors'])

def determine_winner(user, computer):
    if user == computer:
        return "tie"
    
    # Logic: Rock > Scissors, Scissors > Paper, Paper > Rock
    if (user == 'rock' and computer == 'scissors') or \
       (user == 'scissors' and computer == 'paper') or \
       (user == 'paper' and computer == 'rock'):
        return "user"
    
    return "computer"

def main():
    wins = 0
    losses = 0
    ties = 0

    print("--- Rock, Paper, Scissors ---")

    while True:
        user_choice = input("\nEnter rock, paper, or scissors (or 'q' to quit): ").lower()
        
        if user_choice == 'q':
            print(f"\nFinal Score -> You: {wins} | CPU: {losses} | Ties: {ties}")
            break
        
        if user_choice not in ['rock', 'paper', 'scissors']:
            print("Invalid move. Try again.")
            continue

        cpu_choice = get_computer_choice()
        print(f"Computer chose: {cpu_choice}")

        result = determine_winner(user_choice, cpu_choice)
        
        if result == "user":
            print("You Win! 🎉")
            wins += 1
        elif result == "computer":
            print(" Haffa? You Lose! 💀")
            losses += 1
        else:
            print("It's a Tie! 🤝")
            ties += 1

if __name__ == "__main__":
    main()
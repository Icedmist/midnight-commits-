import random

def play_game():
    # 1. Setup State
    secret_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10
    
    print("\nI'm thinking of a number between 1 and 100.")
    print(f"You have {max_attempts} attempts.")

    # 2. Game Loop
    while attempts < max_attempts:
        try:
            guess_txt = input(f"\nAttempt {attempts + 1}: Enter guess: ")
            guess = int(guess_txt)
            attempts += 1

            if guess < secret_number:
                print("Too low!")
            elif guess > secret_number:
                print("Too high!")
            else:
                print(f" Correct! You won in {attempts} attempts.")
                return # Exit the function (ending the game round)

        except ValueError:
            print("Please enter a number.")

    # 3. Game Over Condition
    print(f"\n Game Over! The number was {secret_number}.")

def main():
    while True:
        play_game()
        if input("\nPlay again? (y/n): ").lower() != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
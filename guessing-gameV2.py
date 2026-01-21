import random
import math

# Global High Score (initially infinity so any score beats it)
best_score = float('inf')

def get_difficulty():
    print("\nSelect Difficulty:")
    print("1. Easy (1-50)")
    print("2. Hard (1-100)")
    print("3. Impossible (1-1000)")
    
    choice = input("Choice: ")
    if choice == '1': return 50
    elif choice == '3': return 1000
    else: return 100  # Default to Hard

def play_round():
    global best_score # Access the global variable
    
    limit = get_difficulty()
    secret = random.randint(1, limit)
    attempts = 0
    
    print(f"\nThinking of a number between 1 and {limit}...")
    
    while True:
        try:
            guess = int(input("Your guess: "))
            attempts += 1
            
            if guess < secret:
                print("Too low! ⬆️")
            elif guess > secret:
                print("Too high! ⬇️")
            else:
                print(f"🎉 BOOM! You got it in {attempts} tries.")
                
                # Check for High Score
                if attempts < best_score:
                    best_score = attempts
                    print("🏆 NEW RECORD SET!")
                else:
                    print(f"Current Record: {best_score} tries.")
                break
        except ValueError:
            print("Numbers only, please.")

def main():
    while True:
        play_round()
        if input("\nPlay again? (y/n): ").lower() != 'y':
            print(f"Session ended. Best score today: {best_score if best_score != float('inf') else 'None'}")
            break

if __name__ == "__main__":
    main()
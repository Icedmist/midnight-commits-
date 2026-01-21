import time

def parse_input(user_input):
    """
    Handles formats:
    '1:30' -> 90 seconds
    '2'    -> 2 seconds (default)
    '2m'   -> 120 seconds
    """
    if ':' in user_input:
        mins, secs = user_input.split(':')
        return int(mins) * 60 + int(secs)
    elif 'm' in user_input:
        return int(user_input.replace('m', '')) * 60
    else:
        return int(user_input)

def countdown(seconds):
    total = seconds
    print(f"Timer set for {seconds} seconds.")
    
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        
        # Calculate progress bar
        # Example: [=====     ]
        percent = 1 - (seconds / total)
        bars = int(percent * 20)
        progress = f"[{'=' * bars}{' ' * (20 - bars)}]"
        
        print(f"\r{progress} {mins:02d}:{secs:02d}", end="")
        time.sleep(1)
        seconds -= 1

    # \a is the ASCII Bell character (makes a system sound)
    print("\r[====================] 00:00 \a\a\a") 
    print("\n⏰ WAKE UP!")

def main():
    while True:
        inp = input("\nEnter time (e.g., '1:30', '90', '2m') or 'q': ")
        if inp.lower() == 'q': break
        
        try:
            secs = parse_input(inp)
            countdown(secs)
        except ValueError:
            print("Invalid format.")

if __name__ == "__main__":
    main()
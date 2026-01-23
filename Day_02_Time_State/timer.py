import time

def countdown(seconds):
    print(f"Timer set for {seconds} seconds.")
    
    while seconds > 0:
        # divmod(65, 60) returns (1, 5) -> 1 minute, 5 seconds
        mins, secs = divmod(seconds, 60)
        
        # {:02d} formats numbers to always have 2 digits (e.g., "05")
        timer = f'{mins:02d}:{secs:02d}'
        
        # end="\r" overwrites the same line
        print(timer, end="\r")
        
        time.sleep(1)
        seconds -= 1

    print("00:00")
    print("⏰ Time's up!")

def main():
    while True:
        try:
            inp = input("Enter seconds to count down (or 'q' to quit): ")
            if inp.lower() == 'q':
                break
            
            t = int(inp)
            countdown(t)
            
        except ValueError:
            print("Please enter a valid integer.")

if __name__ == "__main__":
    main()
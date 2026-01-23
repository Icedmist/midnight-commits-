def print_board(board):
    print(f"\n {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} \n")

def check_win(board, player):
    # All 8 winning combinations (indices 0-8)
    # 0 1 2
    # 3 4 5
    # 6 7 8
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), # Horizontal
        (0, 3, 6), (1, 4, 7), (2, 5, 8), # Vertical
        (0, 4, 8), (2, 4, 6)             # Diagonal
    ]
    
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] == player:
            return True
    return False

def is_full(board):
    return " " not in board

def main():
    # Board is a list of 9 spaces
    board = [" "] * 9
    current_player = "X"
    
    print("--- Tic-Tac-Toe ---")
    print("Enter position 1-9 to play.")

    while True:
        print_board(board)
        
        try:
            choice = int(input(f"Player {current_player}, choose (1-9): "))
            if choice < 1 or choice > 9:
                print("Invalid number. Choose 1-9.")
                continue
                
            # Convert 1-9 to 0-8 index
            index = choice - 1
            
            if board[index] != " ":
                print("Space already taken!")
                continue
                
            # Place Mark
            board[index] = current_player
            
            # Check Win
            if check_win(board, current_player):
                print_board(board)
                print(f"🏆 Player {current_player} Wins!")
                break
                
            # Check Draw
            if is_full(board):
                print_board(board)
                print("It's a Draw! 🤝")
                break
            
            # Switch Player
            current_player = "O" if current_player == "X" else "X"
            
        except ValueError:
            print("Please enter a number.")

if __name__ == "__main__":
    main()
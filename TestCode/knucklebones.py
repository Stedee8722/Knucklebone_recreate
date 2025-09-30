import random

boards = [
    [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ],
    [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
]
isGameOver = False

def roll_dice() -> int:
    return random.randint(1, 6)

def check_column_space(board_num: int, column: int) -> bool:
    if board_num in [0, 1] and column in [0, 1, 2]:
        board = boards[board_num]
        column = board[column]
        if 0 in column:
            return True
        else:
            return False
        
def place_dice(board_num: int, column: int, dice: int) -> None:
    if board_num in [0, 1] and column in [0, 1, 2] and dice in [1, 2, 3, 4, 5, 6]:
        board = boards[board_num]
        column = board[column]
        for i in range(len(column)):
            if column[i] == 0:
                column[i] = dice
                break

def check_clash(board_num: int, column: int, dice: int) -> None:
    if board_num in [0, 1] and column in [0, 1, 2] and dice in [1, 2, 3, 4, 5, 6]:
        board = boards[board_num]
        column = board[column]
        if dice in column:
            for i in range(len(column)):
                if column[i] == dice:
                    column[i] = 0

def calc_total(board_num: int) -> int:
    total = 0
    if board_num in [0, 1]:
        for i in range(3):
            total += calc_column_total(board_num, i)
        return total
    else:
        raise ValueError("Board must be 0 or 1, you provided: " + str(board_num))
    
def calc_column_total(board_num: int, column: int) -> int:
    total = 0
    if board_num in [0, 1] and column in [0, 1, 2]:
        board = boards[board_num]
        column = board[column]
        values = [0, 0, 0, 0, 0, 0]
        for value in column:
            if value in [1, 2, 3, 4, 5, 6]:
                values[value - 1] += 1
        for i in range(len(values)):
            if values[i] > 0:
                total += (i + 1) * (values[i] ** 2)
        return total
    else:
        raise ValueError("Board must be 0 or 1 and column must be 0, 1, or 2, you provided board: " + str(board_num) + " and column: " + str(column))
    
def move_dice_down() -> None:
    for board in boards:
        for column in board:
            for i in range(0, 2, 1):
                if column[i] == 0 and column[i + 1] != 0:
                    column[i] = column[i + 1]
                    column[i + 1] = 0

def print_boards() -> None:
    """For debugging purposes only"""
    move_dice_down()
    print(f"       {calc_total(0):02d}")
    print("|--------------|")
    for i in range(2, -1, -1):
        print(f"| {boards[0][0][i]:02d} | {boards[0][1][i]:02d} | {boards[0][2][i]:02d} |")
    print("|--------------|")
    
    print(f"| {calc_column_total(0,0):02d} | {calc_column_total(0,1):02d} | {calc_column_total(0,2):02d} |")

    print("|--------------|")

    print(f"| {calc_column_total(1,0):02d} | {calc_column_total(1,1):02d} | {calc_column_total(1,2):02d} |")

    print("|--------------|")
    for i in range(0, 3, 1):
        print(f"| {boards[1][0][i]:02d} | {boards[1][1][i]:02d} | {boards[1][2][i]:02d} |")
    print("|--------------|")
    print(f"       {calc_total(1):02d}")

def check_game_over() -> None:
    global isGameOver
    if (not 0 in boards[0][0] and not 0 in boards[0][1] and not 0 in boards[0][2]) or (not 0 in boards[1][0] and not 0 in boards[1][1] and not 0 in boards[1][2]):
        isGameOver = True
        print_boards()
        total_0 = calc_total(0)
        total_1 = calc_total(1)
        if total_0 > total_1:
            print("Player 1 wins with a score of " + str(total_0) + " to " + str(total_1) + "!")
        elif total_1 > total_0:
            print("Player 2 wins with a score of " + str(total_1) + " to " + str(total_0) + "!")
        else:
            print("It's a draw!")

def main() -> None:
    board_num = random.randint(0, 1)
    while not isGameOver:
        board_num = 1 - board_num
        dice = roll_dice()
        print_boards()
        place_dice_at = int(input("Choose column (1, 2, 3): \nDice rolled: " + str(dice) + "\nBoard: " + str(board_num + 1) + "\n"))
        place_dice_at -= 1
        check_column_space(board_num, place_dice_at)
        while not check_column_space(board_num, place_dice_at):
            print("Column full or invalid input, choose again.")
            place_dice_at = int(input("Choose column (1, 2, 3): \nDice rolled: " + str(dice) + "\nBoard: " + str(board_num + 1) + "\n"))
            place_dice_at -= 1
            check_column_space(board_num, place_dice_at)
        place_dice(board_num, place_dice_at, dice)
        check_clash(1 - board_num, place_dice_at, dice)
        check_game_over()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import messagebox
import random
from collections import Counter

class FarkleGame:
    def __init__(self, master):
        self.master = master
        master.title("Farkle")

        self.num_players = 0
        self.players = []
        self.current_player_index = 0
        self.current_roll = []
        self.selected_dice_indices = [] # Store indices of selected dice
        self.current_turn_score = 0
        self.dice_in_play = 6 # Number of dice to roll in the current sub-turn

        self.create_widgets()
        self.setup_game() # Call setup_game first

    def create_widgets(self):
        # Main score display frame
        self.all_players_score_frame = tk.Frame(self.master)
        self.all_players_score_frame.pack()

        self.player_score_labels = [] # List to hold labels for each player

        self.turn_score_label = tk.Label(self.master, text="Turn Score: 0", font=("Arial", 14))
        self.turn_score_label.pack(pady=10)

        # Dice display
        self.dice_frame = tk.Frame(self.master)
        self.dice_frame.pack()
        self.dice_buttons = []
        for i in range(6):
            btn = tk.Button(self.dice_frame, text="?", width=5, height=2, command=lambda i=i: self.toggle_die_selection(i))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.dice_buttons.append(btn)

        # Game actions
        self.action_frame = tk.Frame(self.master)
        self.action_frame.pack()

        self.roll_button = tk.Button(self.action_frame, text="Roll Dice", command=self.roll_dice)
        self.roll_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.bank_button = tk.Button(self.action_frame, text="Bank Score", command=self.bank_score, state=tk.DISABLED)
        self.bank_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.end_turn_button = tk.Button(self.action_frame, text="End Turn (Farkle)", command=self.end_turn, state=tk.DISABLED)
        self.end_turn_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.message_label = tk.Label(self.master, text="", font=("Arial", 12), wraplength=400)
        self.message_label.pack(pady=10)

    def setup_game(self):
        # Create a new top-level window for player selection
        self.setup_window = tk.Toplevel(self.master)
        self.setup_window.title("Setup Game")
        self.setup_window.grab_set() # Make this window modal

        tk.Label(self.setup_window, text="Enter number of players (1-4):").pack(pady=10)
        
        self.num_players_entry = tk.Entry(self.setup_window)
        self.num_players_entry.pack(pady=5)
        self.num_players_entry.insert(0, "1") # Default value

        tk.Button(self.setup_window, text="Start Game", command=self._start_game_from_setup).pack(pady=10)

    def _start_game_from_setup(self):
        try:
            num_players = int(self.num_players_entry.get())
            if not 1 <= num_players <= 4:
                raise ValueError("Number of players must be between 1 and 4.")
            self.num_players = num_players
            self.players = [{"name": f"Player {i+1}", "score": 0} for i in range(self.num_players)]
            self.setup_window.destroy()
            self.start_game()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self.setup_window)

    def start_game(self):
        print("--- Game Started ---")
        self.update_display()
        self.roll_dice() # Initial roll

    def process_selected_dice(self):
        temp_selected_dice_values = [self.current_roll[i] for i in self.selected_dice_indices]
        score, used_dice_count = self._get_score_and_used_dice(temp_selected_dice_values)
        
        if score == 0 or used_dice_count != len(temp_selected_dice_values):
            messagebox.showerror("Error", "You must select only scoring dice to continue.")
            self.selected_dice_indices = [] # Clear invalid selection
            self.update_dice_display() # Reset button relief
            self.calculate_current_score() # Update buttons state
            print(f"DEBUG: Invalid dice selection. Score: {score}, Used: {used_dice_count}, Selected: {len(temp_selected_dice_values)}")
            return False # Indicate failure to process

        self.current_turn_score += score
        self.message_label.config(text=f"Scored {score} points this roll. Current turn score: {self.current_turn_score}")
        print(f"DEBUG: Scored {score} points. Current turn score: {self.current_turn_score}")

        # Mark selected dice as used (None) in current_roll
        for index in self.selected_dice_indices:
            self.current_roll[index] = None
        
        self.selected_dice_indices = [] # Clear selected dice for next action

        # Update dice in play
        self.dice_in_play = sum(1 for d in self.current_roll if d is not None)
        self.update_dice_display() # Update display to show used dice as blank
        self.update_display() # Update turn score label

        return True # Indicate successful processing

    def roll_dice(self):
        print(f"\n--- {self.players[self.current_player_index]['name']}'s Turn - Rolling Dice ---")
        self.message_label.config(text="")
        
        # If it's not the very first roll of a turn, process selected dice first
        if self.current_roll and any(d is not None for d in self.current_roll):
            print("DEBUG: Processing previously selected dice before re-roll.")
            if not self.process_selected_dice():
                return # Stop if selected dice are invalid

        # Determine which dice to roll
        dice_to_roll_indices = []
        if not self.current_roll or self.dice_in_play == 0: # First roll of turn or hot dice
            print("DEBUG: First roll of turn or Hot Dice. Rolling all 6 dice.")
            self.current_roll = [None] * 6 # Reset all dice
            for i in range(6):
                dice_to_roll_indices.append(i)
            self.dice_in_play = 6
        else:
            # Re-roll only the dice that are still in play
            print(f"DEBUG: Re-rolling {self.dice_in_play} dice.")
            for i, die_val in enumerate(self.current_roll):
                if die_val is not None:
                    dice_to_roll_indices.append(i)
            self.dice_in_play = len(dice_to_roll_indices)

        # Perform the roll
        for i in dice_to_roll_indices:
            self.current_roll[i] = random.randint(1, 6)
        print(f"DEBUG: Current roll: {self.current_roll}")

        self.selected_dice_indices = [] # Clear selected dice for new roll
        self.update_dice_display()
        
        self.check_for_farkle() # Check for farkle on the new roll
        
        # Re-enable dice buttons for selection
        for i in range(6):
            if self.current_roll[i] is not None:
                self.dice_buttons[i].config(state=tk.NORMAL)
            else:
                self.dice_buttons[i].config(state=tk.DISABLED) # Keep scored dice disabled
        
        self.bank_button.config(state=tk.DISABLED) # Can't bank until something is selected
        self.roll_button.config(state=tk.DISABLED) # Disable roll until dice are selected or farkle

    def toggle_die_selection(self, index):
        print(f"DEBUG: Toggling die selection for index {index} (value: {self.current_roll[index]})")
        # Only allow selection of dice that are currently part of the roll and not already scored
        if self.current_roll[index] is None:
            print("DEBUG: Cannot select already scored/removed die.")
            return

        if index in self.selected_dice_indices:
            self.selected_dice_indices.remove(index)
            self.dice_buttons[index].config(relief=tk.RAISED)
            print(f"DEBUG: Deselected die at index {index}. Selected dice: {self.selected_dice_indices}")
        else:
            self.selected_dice_indices.append(index)
            self.dice_buttons[index].config(relief=tk.SUNKEN)
            print(f"DEBUG: Selected die at index {index}. Selected dice: {self.selected_dice_indices}")
        
        self.calculate_current_score()

    def calculate_current_score(self):
        temp_selected_dice_values = [self.current_roll[i] for i in self.selected_dice_indices]
        score, used_dice_count = self._get_score_and_used_dice(temp_selected_dice_values)
        print(f"DEBUG: Calculating potential score for selected dice {temp_selected_dice_values}. Score: {score}, Used: {used_dice_count}")
        
        # Update turn score display with potential score from selected dice
        self.turn_score_label.config(text=f"Turn Score: {self.current_turn_score + score}")

        if score > 0 and used_dice_count == len(temp_selected_dice_values): # All selected dice are scoreable
            self.bank_button.config(state=tk.NORMAL)
            self.roll_button.config(state=tk.NORMAL) # Allow re-rolling if scoreable dice are selected
            self.end_turn_button.config(state=tk.DISABLED) # Not a farkle if scoreable dice are selected
            print("DEBUG: Valid scoring selection. Bank and Roll enabled.")
        else:
            self.bank_button.config(state=tk.DISABLED)
            self.roll_button.config(state=tk.DISABLED) # Disable roll if no score or not all selected dice are scoreable
            self.end_turn_button.config(state=tk.NORMAL) # Allow ending turn if no score or invalid selection
            print("DEBUG: Invalid scoring selection. Bank and Roll disabled. End Turn enabled.")

    def _get_score_and_used_dice(self, dice_values):
        score = 0
        used_dice_count = 0
        counts = Counter(dice_values)
        
        # Create a mutable copy of dice_values to track remaining dice
        current_dice = list(dice_values) 
        print(f"DEBUG: _get_score_and_used_dice - Input dice_values: {dice_values}")

        # Check for Large Straight (1-2-3-4-5-6) - requires all 6 dice
        if len(dice_values) == 6 and sorted(dice_values) == [1, 2, 3, 4, 5, 6]:
            score += 1500
            used_dice_count += 6
            print("DEBUG: Large Straight detected.")
            return score, used_dice_count

        # Check for Small Straight (e.g., 1-2-3-4-5 or 2-3-4-5-6) - requires 5 consecutive dice
        sorted_unique_dice = sorted(list(set(dice_values)))
        if len(sorted_unique_dice) >= 5:
            is_small_straight = False
            # Check for 1-2-3-4-5
            if all(x in sorted_unique_dice for x in [1,2,3,4,5]):
                is_small_straight = True
            # Check for 2-3-4-5-6
            elif all(x in sorted_unique_dice for x in [2,3,4,5,6]):
                is_small_straight = True

            if is_small_straight:
                score += 1000 # Common house rule for small straight
                used_dice_count += 5 # Assuming 5 dice are used for a small straight
                print("DEBUG: Small Straight detected.")
                # For simplicity, if a small straight is found, we assume all 5 dice are used.
                return score, used_dice_count

        # Check for Three Pairs - requires all 6 dice
        if len(dice_values) == 6 and len(counts) == 3 and all(c == 2 for c in counts.values()):
            score += 1500
            used_dice_count += 6
            print("DEBUG: Three Pairs detected.")
            return score, used_dice_count

        # Score three-of-a-kind, four-of-a-kind, five-of-a-kind, six-of-a-kind
        for i in range(1, 7):
            if counts[i] >= 3:
                if i == 1:
                    score_add = 1000 * (counts[i] - 2) # 3x1 = 1000, 4x1 = 2000, 5x1 = 3000, 6x1 = 4000
                else:
                    score_add = i * 100 * (counts[i] - 2) # 3x = i*100, 4x = i*200, 5x = i*300, 6x = i*400
                score += score_add
                used_dice_count += counts[i]
                print(f"DEBUG: {counts[i]} of a kind ({i}s) detected. Score added: {score_add}")
                # Remove these dice from current_dice
                for _ in range(counts[i]):
                    if i in current_dice:
                        current_dice.remove(i)

        # Score individual 1s and 5s from remaining dice
        for die_val in list(current_dice): # Iterate over a copy as we modify the original
            if die_val == 1:
                score += 100
                used_dice_count += 1
                current_dice.remove(1)
                print("DEBUG: Individual 1 detected. Score added: 100")
            elif die_val == 5:
                score += 50
                used_dice_count += 1
                current_dice.remove(5)
                print("DEBUG: Individual 5 detected. Score added: 50")
        
        print(f"DEBUG: _get_score_and_used_dice - Final score: {score}, Used dice count: {used_dice_count}")
        return score, used_dice_count

    def check_for_farkle(self):
        # Get values of currently unselected dice (those not None in current_roll)
        unselected_dice_values = [d for d in self.current_roll if d is not None]
        print(f"DEBUG: check_for_farkle - Unselected dice values: {unselected_dice_values}")
        
        # If there are no unselected dice, it's a hot dice situation (handled in bank_score)
        # or the turn has ended.
        if not unselected_dice_values:
            print("DEBUG: No unselected dice. Hot dice or turn end.")
            return

        # Check if any scoring combination exists in the unselected dice
        possible_score, _ = self._get_score_and_used_dice(unselected_dice_values)
        print(f"DEBUG: check_for_farkle - Possible score from unselected dice: {possible_score}")

        if possible_score == 0:
            self.message_label.config(text="FARKLE! No scoring dice. Your turn ends and you lose all points for this turn.", fg="red")
            self.current_turn_score = 0
            print("DEBUG: FARKLE detected. Turn score reset to 0.")
            self.end_turn() # End turn immediately on farkle
        else:
            # If there's a possible score, enable roll and bank buttons (bank only if selected)
            self.roll_button.config(state=tk.NORMAL)
            self.bank_button.config(state=tk.DISABLED) # Still disabled until user selects scoring dice
            self.end_turn_button.config(state=tk.NORMAL) # Player can choose to end turn
            print("DEBUG: Possible score from unselected dice. Roll and End Turn enabled.")

    def bank_score(self):
        print("DEBUG: Bank Score button clicked.")
        # Process selected dice before banking
        if not self.process_selected_dice():
            print("DEBUG: Invalid selection, cannot bank.")
            return

        # If it was a hot dice situation, process_selected_dice already handled the message and button states.
        # We only bank the score here and then end the turn.
        self.players[self.current_player_index]["score"] += self.current_turn_score
        self.message_label.config(text=f"Banked {self.current_turn_score} points!") # Overwrite previous message
        print(f"DEBUG: Total banked score for {self.players[self.current_player_index]['name']}: {self.players[self.current_player_index]['score']}")
        self.current_turn_score = 0 # Reset for next turn

        self.check_win()
        # Do not call end_turn() here if it was a hot dice situation. The player should continue their turn.
        # The process_selected_dice method now handles the hot dice logic and button states.
        if self.dice_in_play != 0: # If not hot dice, then end the turn
            print("DEBUG: Not hot dice. Ending turn.")
            self.end_turn()
        else: # If hot dice, reset for next roll in current turn
            print("DEBUG: Hot dice. Resetting for next roll in current turn.")
            self.roll_button.config(state=tk.NORMAL)
            self.bank_button.config(state=tk.DISABLED)
            self.end_turn_button.config(state=tk.NORMAL)

    def end_turn(self):
        print("DEBUG: End Turn button clicked.")
        # Only bank current_turn_score if it's not a farkle
        if self.message_label.cget("text") != "FARKLE! No scoring dice. Your turn ends and you lose all points for this turn.":
            self.players[self.current_player_index]["score"] += self.current_turn_score
            print(f"DEBUG: Banking remaining turn score: {self.current_turn_score}")
            self.check_win() # Check for win condition after banking

        self.current_turn_score = 0
        self.current_roll = [] # Clear current roll for next player
        self.selected_dice_indices = []
        self.dice_in_play = 6
        self.update_dice_display()
        self.update_display()
        self.roll_button.config(state=tk.NORMAL)
        self.bank_button.config(state=tk.DISABLED)
        self.end_turn_button.config(state=tk.DISABLED)
        print("DEBUG: Turn ended. Moving to next player.")
        self.next_player()

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print(f"DEBUG: Next player is {self.players[self.current_player_index]['name']}")
        self.update_display()
        self.roll_dice() # Start next player's turn

    def check_win(self):
        if self.players[self.current_player_index]["score"] >= 10000:
            messagebox.showinfo("Game Over", f"{self.players[self.current_player_index]['name']} wins!")
            print(f"DEBUG: Game Over! {self.players[self.current_player_index]['name']} wins with {self.players[self.current_player_index]['score']} points.")
            self.master.quit() # End game

    def update_display(self):
        # Clear existing player score labels
        for widget in self.all_players_score_frame.winfo_children():
            widget.destroy()
        self.player_score_labels = []

        for i, player in enumerate(self.players):
            player_text = f"{player['name']}: {player['score']}"
            if i == self.current_player_index:
                player_label = tk.Label(self.all_players_score_frame, text=player_text, font=("Arial", 12, "bold"), fg="blue")
            else:
                player_label = tk.Label(self.all_players_score_frame, text=player_text, font=("Arial", 12))
            player_label.pack(side=tk.LEFT, padx=10)
            self.player_score_labels.append(player_label)
        print(f"DEBUG: Display updated. Current player: {self.players[self.current_player_index]['name']}, Scores: {[p['score'] for p in self.players]}")

        self.turn_score_label.config(text=f"Turn Score: {self.current_turn_score}")

    def update_dice_display(self):
        for i, die_val in enumerate(self.current_roll):
            if die_val is None: 
                self.dice_buttons[i].config(text="", relief=tk.FLAT, state=tk.DISABLED)
            else:
                self.dice_buttons[i].config(text=str(die_val), relief=tk.RAISED, state=tk.NORMAL)
        
        # Disable selected dice for next roll within the same turn
        for i in self.selected_dice_indices:
            self.dice_buttons[i].config(state=tk.DISABLED)
        print(f"DEBUG: Dice display updated. Current dice: {self.current_roll}")


root = tk.Tk()
game = FarkleGame(root)
root.mainloop()
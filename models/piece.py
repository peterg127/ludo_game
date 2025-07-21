class Piece:
    def __init__(self, color, id, location, position):
        self.color = color
        self.id = id
        self.location = location # home, safe_zone, board
        self.position = position # specific position within the location
        self.move_counter = 0
        

    def increment_move_counter(self, dice_roll):
        self.move_counter += dice_roll

    def can_move_to_safe_zone(self, dice_roll):
        new_position = self.move_counter + dice_roll
        if new_position >= 40:
            return True
        return False
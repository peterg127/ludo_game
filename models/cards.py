import random

class Card:
    def __init__(self, id, name, effect):
        self.id = id
        self.name = name
        self.effect = effect

    def move_forward():
        steps = random.randint(3)
        return steps

    def move_back():
        steps = random.randint()
        return steps

    def serialize_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "effect": self.effect,
        }

    def change_text(self):
        if self.effect < 0:
            self.name = f"Move back by {abs(self.effect)} squares!"
        else:
            self.name = f"Move forward by {self.effect} squares!"

blessed_cards = [
    Card(1, "Move Three Squares Forward", None),
    #Card(2, "Extra Turn", None),  # Implement logic
    #Card(3, "Shield from Cursed", None),  # Implement logic
]

cursed_cards = [Card(4, "Go back to home! ", None), Card(5, "backward move", None)]

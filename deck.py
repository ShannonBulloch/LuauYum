import random

from card import *


def initialize_deck():
    deck = []
    for _ in range(6):
        deck.append(SpamMusubi(1))
    for _ in range(12):
        deck.append(SpamMusubi(2))
    for _ in range(8):
        deck.append(SpamMusubi(3))

    for _ in range(14):
        deck.append(Manapua())

    for _ in range(10):
        deck.append(Haupia())

    for _ in range(6):
        deck.append(CoconutFlakes())

    for _ in range(4):
        deck.append(PlateLunch())

    for _ in range(14):
        deck.append(KaluaPork())
        deck.append(AhiPoke())

    for _ in range(5):
        deck.append(Banana())
        deck.append(Pineapple())

    for _ in range(10):
        deck.append(Papaya())

    random.shuffle(deck)
    return deck


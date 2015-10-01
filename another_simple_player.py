from player import Player
from card import *


class SimpleTwo(Player):
    cards_seen = []
    ROUNDS = [1, 2, 3]
    current_round = ROUNDS[0]
    current_turn = 0
    total_num_players = None

    # thresholds are number of cards that must be remaining in the
    # player's hand in order to select the card on the turn
    coconut_threshold = 3
    plate_lunch_threshold = 4
    pork_turn_threshold = 4
    # must have at least this many cards left to pick AhiPoke if none are on the table
    ahi_turn_threshold_none = 6
    # must have at least this many cards left to pick AhiPoke if only one is on the table
    ahi_turn_threshold_one = 5

    def get_card_to_play(self, all_table_cards, haupia_counts):

        if self.table_cards.get(PlateLunch.PLATE_LUNCH):
            # if dictionary has PlateLunch, check to see if it should be played this round
            cards = self.pick_plate_lunch_cards()
            if cards:
                return cards
        if len(self.hand) >= self.coconut_threshold and self.hand.__contains__(CoconutFlakes()):
            return CoconutFlakes()
        if len(self.hand) >= self.plate_lunch_threshold and self.hand.__contains__(PlateLunch()):
            return PlateLunch()

        # if Coconut Flakes on table, look for highest Fruit card.
        # if it's Pineapple, play that card, otherwise wait to see if we can play a higher scoring card
        fruit = None
        if self.table_cards.get(CoconutFlakes.COCONUT_FLAKES):
            for possible_card in self.hand:
                if isinstance(possible_card, Fruit):
                    if not fruit:
                        fruit = possible_card
                    else:
                        if possible_card.get_points() > fruit.get_points():
                            fruit = possible_card

            if isinstance(fruit, Pineapple):
                return fruit

        card = self.find_card_to_complete_set(self.hand)
        if card:
            return card



        ahi_poke = AhiPoke()
        if self.hand.__contains__(ahi_poke):
            # if no ahi on the table, check that cards remaining meet threshold
            ahi_on_table = self.table_cards.get(ahi_poke.name, [])
            if not ahi_on_table and len(self.hand) >= self.ahi_turn_threshold_none:
                return ahi_poke
            elif (len(self.table_cards.get(ahi_poke)) % ahi_poke.num_req >= 1 and len(
                    self.hand) >= self.ahi_turn_threshold_one):
                # ahi on the table in incomplete set, and the number of cards left meets the threshold
                return ahi_poke



        kalua_pork = KaluaPork()
        if self.hand.__contains__(kalua_pork):
            pork_on_table = self.table_cards.get(kalua_pork.name, [])
            # if there isn't any pork, or only complete sets, make sure cards left meets threshold
            if len(pork_on_table) % kalua_pork.num_req == 0 and len(self.hand) >= self.pork_turn_threshold:
                return kalua_pork



    def pick_plate_lunch_cards(self):
        """
        Determines if PlateLunch card should be used this turn.
        Uses simplified logic to determine if there are 2 cards worth swapping for
        :return: list of 2 cards to play, or None if PlateLunch not used
        """
        # Good cards to use it on:
        # CoconutFlakes and a Papaya or Pineapple
        # Papaya or Pineapple and something else if CoconutFlakes on the table
        # 2 KaluaPork cards
        # Card that completes set and another card that's worth points
        # (e.g. KuluaPork if another is on the table and a SpamMusubi, Fruit, or Manapua card)
        # 2 SpamMusubi cards if total rolls >= 4
        # 2 AhiPoke if there are several turns left to get the 3rd
        # if there are only 2 cards left in the player's hand, then use regardless

        if self.hand.__contains__(Papaya()) or self.hand.__contains__(Pineapple()):
            if self.hand.__contains__(CoconutFlakes()):
                # CoconutFlakes and a Papaya or Pineapple
                return [CoconutFlakes(), Pineapple() if self.hand.__contains__(Pineapple()) else Papaya()]
            elif self.table_cards.get(CoconutFlakes.COCONUT_FLAKES):
                # Papaya or Pineapple and something else if CoconutFlakes on the table
                first_card = Pineapple() if self.hand.__contains__(Pineapple) else Papaya()
                second_card = self.get_second_plate_lunch_card(first_card)
                if second_card:
                    return [first_card, second_card]

        # 2 KaluaPork cards
        if self.hand.count(KaluaPork()) >= 2:
            return [KaluaPork(), KaluaPork()]

        # Card that completes set and another card that's worth points
        # (e.g. KuluaPork if another is on the table and a SpamMusubi, Fruit, or Manapua card)
        first_card = self.find_card_to_complete_set(self.hand)
        if first_card:
            second_card = self.get_second_plate_lunch_card(first_card)
            if second_card:
                return [first_card, second_card]

        # 2 SpamMusubi cards if both cards have rolls >=2
        musubis = []
        for card in self.hand:
            if isinstance(card, SpamMusubi) and card.num_rolls >= 2:
                musubis.append(card)
        if len(musubis) >= 2:
            musubis = sorted(musubis, key=lambda musubi: musubi.num_rolls, reverse=True)
            return musubis[:2]

        # 2 AhiPoke if there are several turns left to get the 3rd
        if self.hand.count(AhiPoke()) >= 2 and len(self.hand) >= self.ahi_turn_threshold_none:
            return [AhiPoke(), AhiPoke()]

        # if there are only 2 cards left in the player's hand, then use regardless
        if len(self.hand) == 2:
            return self.hand

        return None

    def get_second_plate_lunch_card(self, first_card):
        """
        Tries to find a good second card for plate lunch.
        :return: Second card to play, or None if no good cards were found
        (may result in PlateLunch not being used this turn)
        """
        hand = self.hand.copy()
        hand.remove(first_card)
        if len(hand) == 0:
            return None

        # check to see if table had incomplete set (e.g. 2 AhiPoke) and hand has card to complete it
        second_card = self.find_card_to_complete_set(hand)
        if second_card:
            return second_card
        max_card = hand[0]
        for card in hand[1:]:
            if card.get_points() > max_card.get_points():
                max_card = card

        points_threshold = 1
        if max_card.get_points() >= points_threshold:
            return max_card

        return None

    def find_card_to_complete_set(self, hand):
        """
        Checks to see if the table has incomplete set (1 KaluaPork or 2 AhiPoke) and if the hand can complete it
        :return: Card to complete set if it exists, or None
        """
        ahi_poke = AhiPoke()
        if self.table_cards.get(ahi_poke.name) and len(
                self.table_cards.get(ahi_poke.name)) % ahi_poke.num_req == 2 and hand.__contains__(
            ahi_poke):
            return ahi_poke

        kalua_pork = KaluaPork()
        if self.table_cards.get(kalua_pork.name) and len(
                self.table_cards.get(kalua_pork.name)) % kalua_pork.num_req == 1 and hand.__contains__(kalua_pork):
            return kalua_pork

        return None

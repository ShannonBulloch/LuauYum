import random

from card import SpamMusubi, CoconutFlakes, PlateLunch, Fruit


def print_table_cards(table_cards):
    for key, value in table_cards.items():
        if key == SpamMusubi.SPAM_MUSUBI:
            count = len(value[0])
            print('\t{}x {}. Total rolls: {}'.format(count, key, value[1]))
        elif key in Fruit.FRUITS:
            count = 0
            coconut_count = 0
            for card in value:
                if card.coconut_flakes:
                    coconut_count += 1
                else:
                    count += 1
            if coconut_count > 0:
                print('\t{}x {} with Coconut Flakes'.format(coconut_count, key))
            if count > 0:
                print('\t{}x {}'.format(count, key))
        else:
            count = len(value)
            print('\t{}x {}'.format(count, key))


class Player(object):
    # set of cards, I don't care about the order
    # nevermind, I need to allow duplicates, so it can be a list
    # or a map of card -> count

    def __init__(self, player_num, player_name=None):
        self.player_num = player_num
        self.player_name = player_name if player_name else 'Computer Player ' + str(player_num + 1)
        self.table_cards = {}
        self.hand = []
        self.haupias = 0
        self.score = 0

    def play_card(self, all_table_cards, haupia_counts):
        """ Play a card.
        Selects a card from the player's hand according to the player's
        get_card_to_play() method and adds it to the player's table cards.
        :param all_table_cards:
        :param haupia_counts:
        :return: Whether or not to keep playing the game
        """
        cards = self.get_card_to_play(all_table_cards, haupia_counts)
        if not cards:
            return False

        if len(cards) > 1:
            # find plate lunch card from table and add it back to the players hand
            plate_lunch = self.table_cards.get(PlateLunch.PLATE_LUNCH)
            if not plate_lunch:
                # throw an error?
                # hack for now:
                # edit cards returned from get_card_to_play so that there's only 1 card
                if cards and len(cards) > 1:
                    cards = [cards[0]]
                # remove 'Plate Lunch' key from dictionary if it exists
                if self.table_cards.keys().__contains__(PlateLunch.PLATE_LUNCH):
                    self.table_cards.pop(PlateLunch.PLATE_LUNCH)
            else:
                self.hand.append(plate_lunch.pop())
                if len(plate_lunch) == 0:
                    # last Plate Lunch card, remove it from the dictionary
                    self.table_cards.pop(PlateLunch.PLATE_LUNCH)
        elif isinstance(cards[0], Fruit):
            # check table cards for CoconutFlakes, and play the Fruit on the CoconutFlakes
            coconut_flakes = self.table_cards.get(CoconutFlakes.COCONUT_FLAKES)
            if coconut_flakes:
                cards[0].coconut_flakes = coconut_flakes.pop()
                if len(coconut_flakes) == 0:
                    # last CoconutFlakes card, remove it from the dictionary
                    self.table_cards.pop(CoconutFlakes.COCONUT_FLAKES)

        for card in cards:
            self.add_played_card_to_table(card)
        return True

    def add_played_card_to_table(self, played_card):
        if played_card:
            if played_card.name == SpamMusubi.SPAM_MUSUBI:
                cards, musubi_count = self.table_cards.get(SpamMusubi.SPAM_MUSUBI, ([], 0))
                cards.append(played_card)
                musubi_count += played_card.num_rolls
                self.table_cards.update({SpamMusubi.SPAM_MUSUBI: (cards, musubi_count)})
            else:
                same_cards = self.table_cards.get(played_card.name, [])
                same_cards.append(played_card)
                self.table_cards.update({played_card.name: same_cards})
            self.hand.remove(played_card)
            return True
        else:
            return False

    def get_card_to_play(self, all_table_cards, haupia_counts):
        """Gets card(s) to play. Will always return a list.
        If the player is using PlateLunch on this turn, the list will contain
        the 2 cards played, otherwise the list will have only one card
        :param all_table_cards: list of dictionaries of each player's table cards.
        In the dictionary, the key is the card name and the value is a list
        of the Card objects the player has
        :param haupia_counts: list of each player's haupia counts (from previous rounds)
        """
        # should be implemented by subclasses according to their strategy
        raise NotImplementedError('Please Implement this method')


class SimplePlayer(Player):
    # will use the simple strategy of picking random cards to play

    def get_card_to_play(self, all_table_cards, haupia_counts):
        return [self.hand[random.randint(0, len(self.hand)-1)]]


class Human(Player):
    # real player will select card via the terminal/UI

    def __init__(self, player_num):
        super().__init__(player_num, 'Human Player')

    def get_card_to_play(self, all_table_cards, haupia_counts):
        print('TABLE CARDS')

        for index, table_cards in enumerate(all_table_cards):
            if index != self.player_num:
                print('Player {}:'.format(index + 1))
                print_table_cards(table_cards)
                print('\tPlus {} Haupias from previous rounds'.format(haupia_counts[index]))

        print('='*30)
        print('Your cards on the table:')
        print_table_cards(self.table_cards)
        print('\tPlus {} Haupias from previous rounds'.format(self.haupias))
        print('='*30)

        while True:
            selection = self.get_user_selection()
            if selection.lower() == 'q':
                return None
            elif selection.lower() == 'plate lunch':
                card_one = self.get_plate_lunch_card_selection('First')
                card_two = self.get_plate_lunch_card_selection('Second')
                return [card_one, card_two]
            else:
                try:
                    card_index = int(selection)
                except ValueError:
                    print("\nThat's not a number")
                    continue

                if 0 <= card_index < len(self.hand):
                    return [self.hand[card_index]]

    def get_user_selection(self):
        print('Your hand:')
        for index, card in enumerate(self.hand):
            print('[{}] {}'.format(index, card))

        if self.table_cards.get(CoconutFlakes.COCONUT_FLAKES):
            print('\nYou have a Coconut Flakes card, so if you play a Fruit it'
                  ' will be played on top of the Coconut Flakes and get a x3 bonus')

        if self.table_cards.get(PlateLunch.PLATE_LUNCH):
            print("\nYou have a Plate Lunch card. To use it to swap for 2 cards"
                  " in your hand enter 'plate lunch'")

        selection = input('\nWhich card would you like to play? Enter the number.\n> ')
        return selection

    def get_plate_lunch_card_selection(self, first_or_second):
        prompt = '\n{} card to use with Plate Lunch? Enter the number.\n> '
        while True:
            selection = input(prompt.format(first_or_second))
            if selection.lower() == 'q':
                return None
            try:
                card_index = int(selection)
            except ValueError:
                print("\nThat's not a number")
                continue

            if 0 <= card_index < len(self.hand):
                return self.hand[card_index]

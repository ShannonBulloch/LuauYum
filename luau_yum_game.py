import random

from card import *
from player import *


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


def initialize_players(num_players):
    players = []
    for num in range(num_players - 1):
        players.append(SimplePlayer(num))
    players.append(Human(num_players - 1))
    return players


class Game(object):
    def __init__(self, num_players=3):
        self.num_players = num_players
        self.deck = initialize_deck()
        self.players = initialize_players(num_players)

    def play_game(self):
        finished_game = True
        for round_num in range(1,4):
            keep_playing = self.play_round(round_num)
            if not keep_playing:
                finished_game = False
                break
            # print scores at end of round
            
            # clear table cards
            for player in self.players:
                player.table_cards = {}
        
        if finished_game:
            # score the game. First add in haupia scores, then sort players by total score
            self.score_haupia()
            ranked_players = sorted(self.players, key=lambda player1: player1.score)[::-1]
            print('{} wins with {} points!'.format(ranked_players[0].player_name, ranked_players[0].score))
            print("Here's how everyone else did:")
            for rank, player in enumerate(ranked_players[1:]):
                print('{}. {}, {} points'.format(rank+2, player.player_name, player.score))
    
    def play_round(self, round_num):
        # e.g. 3 player game, 9 cards each. 4 player game, 8 cards each
        cards_per_player = 12 - self.num_players
        self.deal_cards(round_num, cards_per_player)

        # call player.play_card for each player, then pass the cards,
        # until all cards played
        for _ in range(cards_per_player):
            (played_cards, haupia_counts) = self.get_players_table_cards()
            for player in self.players:
                keep_playing = player.play_card(played_cards, haupia_counts)
            if not keep_playing:
                break    
            self.pass_cards()
        
        # score the round
        self.score_round()
        self.print_round_scores()
        return keep_playing
    
    def deal_cards(self, round_num, cards_per_player):
        cards_per_round = cards_per_player * self.num_players

        start_index = (round_num - 1) * cards_per_round
        end_index = start_index + cards_per_round
        for player in self.players:
            start = start_index + player.player_num
            player.hand = self.deck[start:end_index:self.num_players]

    def pass_cards(self):
        """Pass each hand to the next player"""
        
        last_hand = list(self.players[-1].hand)
        # start with the last player
        # pass the hand from the preceding player up to the next player
        for player in self.players[::-1]:
            # first player is the wrap around case. gets the last_hand we got earlier
            if player == self.players[0]:
                player.hand = last_hand
            else:
                player.hand = list(self.players[self.players.index(player)-1].hand)

    def get_players_table_cards(self):
        """Returns all table cards as a tuple of (list of player.table_cards, list of haupia counts)
        Here the haupia counts are haupias from previous rounds
        """
        played_cards = []
        haupia_counts = []
        for player in self.players:
            table_cards_copy = {}
            for key, value in player.table_cards.items():
                if key == SpamMusubi.SPAM_MUSUBI:
                    table_cards_copy.update({key: (list(value[0]), value[1])})
                else:
                    table_cards_copy.update({key: list(value)})
            played_cards.append(table_cards_copy)
            haupia_counts.append(player.haupias)
        return played_cards, haupia_counts

    def score_round(self):
        # score each hand, except for the SpamMusubi cards
        # keep dictionary of count -> list of players
        # then determine most and second most musubi
        musubi_counts = {}

        for player in self.players:
            score = 0
            for key, value in player.table_cards.items():
                if key == SpamMusubi.SPAM_MUSUBI:
                    # value here is tuple (cards, count of SpamMusubi rolls) for the player
                    musubi_count = value[1]
                    players_with_count = musubi_counts.get(musubi_count,[])
                    players_with_count.append(player)
                    musubi_counts.update({musubi_count:players_with_count})
                elif key == Haupia.__name__:
                    # value here is list of Haupia cards
                    count = len(value)
                    player.haupias += count
                else:
                    list_cards = value
                    # if list of cards are KaluaPork or AhiPoke,
                    # get points for the groups of cards
                    if list_cards and isinstance(list_cards[0],CardWithMinimum):
                        score += list_cards[0].get_points(list_cards)
                    else:
                        # otherwise, get points for each card in list
                        for card in list_cards:
                            score += card.get_points()
            player.score += score

        # find most and second most spam musubi
        if musubi_counts:
            most_musubi = musubi_counts.pop(max(musubi_counts))
            for player in most_musubi:
                player.score += SpamMusubi.get_points(SpamMusubi.FIRST, len(most_musubi), len(most_musubi) > 1)
            # if there are still players with musubi, find the second most
            if musubi_counts:
                second_musubi = musubi_counts.pop(max(musubi_counts))
                for player in second_musubi:
                    player.score += SpamMusubi.get_points(SpamMusubi.SECOND, len(second_musubi), len(most_musubi) > 1)

    def print_round_scores(self):
        print('\n Scores after that round:\n')
        for player in self.players:
            print('\t{}, {} points'.format(player.player_name, player.score))
        print('\n')

    def score_haupia(self):
        haupia_counts = {}
        
        for player in self.players:
            count = player.haupias
            players_with_count = haupia_counts.get(count,[])
            players_with_count.append(player)
            haupia_counts.update({count:players_with_count})
        # find most and least haupias
        most_haupia = haupia_counts.pop(max(haupia_counts))
        for player in most_haupia:
            player.score += Haupia.get_points(Haupia.MOST, len(most_haupia))
        
        least_haupia = haupia_counts.pop(min(haupia_counts))
        for player in least_haupia:
            player.score += Haupia.get_points(Haupia.LEAST, len(least_haupia))


g = Game()
g.play_game()
from math import floor


class Card(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.__class__.__name__)
        self.value = kwargs.get('value', None)

    def get_points(self, *args):
        raise NotImplementedError('Please Implement this method')

    def get_info(self):
        return '{}, {}'.format(self.name, self.value)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)


class SpamMusubi(Card):
    # Spam Musubi
    # 6, 1 roll cards
    # 12, 2 roll cards
    # 8, 3 roll cards
    SPAM_MUSUBI = 'Spam Musubi'
    
    FIRST = 1
    SECOND = 2

    SCORE_FIRST = 6
    SCORE_SECOND = 3

    def __init__(self, num_rolls):
        super().__init__(name='Spam Musubi')
        self.num_rolls = num_rolls
    
    def get_points(self, player_rank, num_players=1, first_place_tie=False):
        return self.get_points(player_rank, num_players, first_place_tie)
    
    def get_points(player_rank, num_players=1, first_place_tie=False):
        if player_rank == SpamMusubi.FIRST:
            return floor(SpamMusubi.SCORE_FIRST/num_players)
        elif player_rank == SpamMusubi.SECOND and not first_place_tie:
            # if there is a tie for first,
            # only those players get points for spam musubi
            return floor(SpamMusubi.SCORE_SECOND/num_players)
        else:
            return 0

    def get_info(self):
        return '{}, Most {}, Second Most {}'.format(self.name,
                                                    str(self.SCORE_FIRST),
                                                    str(self.SCORE_SECOND))

    def __str__(self):
        return '{} {}'.format(self.name, self.num_rolls)
    
    def __repr__(self):
        return '{} {}'.format(self.name, self.num_rolls)


class Manapua(Card):
    # Manapua
    # 14
    POINTS = [1, 3, 6, 10, 15]

    def get_points(self, num_cards=1):
        if num_cards > len(self.POINTS):
            return self.POINTS[-1]
        else:
            return self.POINTS[num_cards-1]        

    def get_info(self):
        info = '{}'.format(self.name)
        for index, points in enumerate(self.POINTS):
            if index < 4:
                info = info + ', x{}={}'.format(index+1, points)
            else:
                info = info + ', x{}+={}'.format(index+1, points)
        return info

class Haupia(Card):
    # Haupia
    # 10
    MOST = 1
    LEAST = -1

    SCORE_MOST = 6
    SCORE_LEAST = -6

    def get_points(self, player_rank, num_players=1):
        return self.get_points(player_rank, num_players)

    def get_points(player_rank, num_players=1):
        if player_rank == Haupia.MOST:
            return floor(Haupia.SCORE_MOST/num_players)
        elif player_rank == Haupia.LEAST:
            return floor(Haupia.SCORE_LEAST/num_players)
        else:
            return 0

    def get_info(self):
        return ('{}. At end of 3 rounds:'
                ' Most {}, Least {}'.format(self.name, self.SCORE_MOST,
                                            self.SCORE_LEAST))


class CoconutFlakes(Card):
    # Coconut (to decorate fruit)
    # 6
    COCONUT_FLAKES = 'Coconut Flakes'
    BONUS = 3

    def __init__(self):
        super().__init__(name=self.COCONUT_FLAKES)

    def get_points(self):
        return 0

    def get_info(self):
        return '{}, Next {} x{}'.format(self.name, Fruit.__name__, self.BONUS)


class PlateLunch(Card):
    PLATE_LUNCH = 'Plate Lunch'
    # 4

    def __init__(self):
        super().__init__(name=self.PLATE_LUNCH)

    def get_points(self):
        return 0

    def get_info(self):
        return '{}, Swap for 2 cards'.format(self.name)


class CardWithMinimum(Card):
    def __init__(self, name, value, num_req):
        # value will store possible value if number of cards needed
        # to get score is achieved. E.g. KaluaPork will have value=5, but
        # player must have 2 cards in order to get the points
        super().__init__(name=name, value=value)
        self.num_req = num_req

    def get_points(self, cards_same_type=None):
        if not cards_same_type:
            return 0
        num_of_groups = floor(len(cards_same_type)/cards_same_type[0].num_req)
        return num_of_groups * cards_same_type[0].value

    def get_info(self):
        return '{}, x{}={}'.format(self.name, self.num_req, self.value)


class KaluaPork(CardWithMinimum):
    # Kalua Pork
    # 14
    def __init__(self):
        super().__init__('Kalua Pork', 5, 2)


class AhiPoke(CardWithMinimum):
    # Teriyaki Chicken, Ahi Poke?
    # 14
    def __init__(self):
        super().__init__('Ahi Poke', 10, 3)


class Fruit(Card):
    # Fruit
    FRUITS = ['Banana', 'Papaya', 'Pineapple']

    bonus = 1
    coconut_flakes = None

    def get_points(self):
        return self.value * (self.coconut_flakes.BONUS if self.coconut_flakes else 1)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class Banana(Fruit):
    # Banana
    # 5
    def __init__(self):
        super().__init__(name='Banana', value=1)


class Papaya(Fruit):
    # Papaya
    # 10
    def __init__(self):
        super().__init__(name='Papaya', value=2)


class Pineapple(Fruit):
    # Pineapple
    # 5
    def __init__(self):
        super().__init__(name='Pineapple', value=3)

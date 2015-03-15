#!/usr/bin/python
#
# ginmatch.py
#
# 2015/03/15
# rg
#
# class to run a match of gin. a match consists of multiple GinGames, scoring as follows:
#
# win by knock: winner gets points equal to difference in deadwood held by both players
# win by gin: winner gets deadwood of loser + 25 points
# win by undercut: winner gets points equal to difference in deadwood held by both players + 25 points
#
# In the case that a player knocks or calls gin and does not have a valid knocking/gin hand, that hand
# will be exposed and visible to the opponent for the remainder of the game.
#
# once a score of 100 is reached, final scoring occurs as follows:
# - first player to 100 receives 'game bonus' of 100 points
# - both players are granted a 20 point 'line bonus' for each game won
# - totals are tallied. highest score wins.
#
# In the case that the final scores are equal, we flip a coin. In the real world, we'd want a re-match. In
# the world we're playing with here, there's a good chance we'll have identical strategies facing each other
# with an exaggerated chance of duplicate scores, leading to a good chance of infinite recursion. There will
# be other, similar if not identical strategies floating about in the population, so we can safely prune out
# ties without worrying about a large genetic penalty.

import random
from gintable import *
from ginplayer import *
from gindeck import *


class GinMatch:
    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2

        # players may now be seated
        self.table = GinTable()
        self.table.seat_player(self.p1)
        self.table.seat_player(self.p2)
        self.p1_score = 0
        self.p2_score = 0
        self.p1_matches_won = 0
        self.p2_matches_won = 0

    # run the match until a winner is declared
    def run(self):
        # continue playing games until one player reaches 100
        while self.p1_score < 100 and self.p2_score < 100:
            self.play_game()

        # perform final scoring
        # - calculate game bonus
        if self.p1_score >= 100:
            self.p1_score += 100
        elif self.p2_score >= 100:
            self.p2_score += 100

        # - calculate line bonus
        self.p1_score += 20 * self.p1_matches_won
        self.p2_score += 20 * self.p2_matches_won

        # return winner
        if self.p1_score > self.p2_score:
            return self.p1
        elif self.p2_score > self.p1_score:
            return self.p2
        else:
            # tie: flip a coin to determine winner
            if random.random() < 0.5:
                return self.p1
            else:
                return self.p2

    # play one game of gin
    def play_game(self):

        # deal 10 cards to each player
        for i in range(10):
            self.p1.draw()
            self.p2.draw()

        # deal an 11th card to first player
        self.p1.draw()
        pass

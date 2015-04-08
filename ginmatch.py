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

from gintable import *
from ginplayer import *


class GinMatch(Observable):
    def __init__(self, player1, player2):
        """ @type p1: GinPlayer
            @type p2: GinPlayer
        """
        super(GinMatch, self).__init__()

        # rules
        self.knocking_point = 10

        # set up score board
        self.p1_score = 0
        self.p2_score = 0
        self.p1_matches_won = 0
        self.p2_matches_won = 0

        # seat players (not randomly)
        self.table = GinTable()
        self.p1 = player1
        self.p2 = player2
        self.table.seat_player(self.p1)
        self.table.seat_player(self.p2)

        # track game state
        self.gameover = False
        self.player_who_knocked = False
        self.player_who_knocked_gin = False
        self.p1_knocked_improperly = False
        self.p2_knocked_improperly = False

        # coordinate knocks with each player
        self.p1.register_knock_listener(self)
        self.p1.register_knock_gin_listener(self)
        self.p2.register_knock_listener(self)
        self.p2.register_knock_gin_listener(self)

    def notify_of_knock(self, knocker):
        self.player_who_knocked = knocker

    def notify_of_knock_gin(self, knocker):
        self.player_who_knocked_gin = knocker

    # implement the Observable criteria. return a list of ints representing our game state
    def organize_data(self):
        data = []


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
        else:
            raise ValueError("score must be 100+ for endgame. scores are p1:%s p2:%s" % self.p1_score, self.p2_score)

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

        # clear game states
        self.gameover = False
        self.player_who_knocked_gin = False
        self.player_who_knocked = False
        self.p1_knocked_improperly = False
        self.p2_knocked_improperly = False

        # play one game
        self.deal_cards()
        self.take_turns()
        self.update_score()

    # deal out 11 cards to p1 and 10 cards to p2
    def deal_cards(self):
        # deal 10 cards to each player
        for i in range(10):
            self.p1.draw()
            self.p2.draw()

        # deal an 11th card to first player
        self.p1.draw()

    # alternate play between each player
    def take_turns(self):
        # beginning with p1, take turns until a valid knock/gin is called OR we have only two cards remaining
        while not self.gameover and len(self.table.deck.cards) >= 2:
            # both players get a chance to play, respecting knocks and end-of-game notifications
            for p in (self.p1, self.p2):
                # exit condition
                if not self.gameover:
                    p.take_turn()

                    # validate the knock or reset the knock state and penalize the knocker
                    if self.player_who_knocked:
                        if p.hand.deadwood_count() <= 10:
                            self.end_with_knock(p)
                        else:
                            self.player_who_knocked = False
                            if p == self.p1:
                                self.p1_knocked_improperly = True
                            elif p == self.p2:
                                self.p2_knocked_improperly = True

                    # validate the knock_gin or penalize the knocker and reset the knock state
                    elif self.player_who_knocked_gin:
                        if p.hand.deadwood_count != 0:
                            self.end_with_knock_gin(p)
                        else:
                            self.player_who_knocked_gin = False
                            if p == self.p1:
                                self.p1_knocked_improperly = True
                            elif p == self.p2:
                                self.p2_knocked_improperly = True

    # award deadwood scoring and gin bonuses
    def update_score(self):
        score_delta = 0

        # track the 'defender' of the knock/gin
        if self.p1 == self.player_who_knocked:
            defender = self.p2
            knocker = self.p1
        else:
            defender = self.p1
            knocker = self.p2

        # for gin, no lay-offs
        if self.player_who_knocked_gin:
            # points for defender's deadwood
            score_delta += defender.hand.deadwood_count()

            # 25 bonus points for gin
            score_delta += 25

            # update score tallies
            if knocker == self.p1:
                self.p1_score += score_delta
            elif knocker == self.p2:
                self.p2_score += score_delta

        # for knocks, allow lay-offs
        elif self.player_who_knocked:
            defender_deadwood = defender.hand.deadwood_count()
            knocker_deadwood = knocker.hand.deadwood_count()
            score_delta = abs(knocker_deadwood - defender_deadwood)

            # check for undercuts
            if defender_deadwood <= knocker_deadwood:
                score_delta += 25
                if knocker == self.p1:
                    self.p2_score += score_delta
                elif knocker == self.p2:
                    self.p1_score += score_delta
            # regular knocks
            else:
                if knocker == self.p1:
                    self.p1_score += score_delta
                elif knocker == self.p2:
                    self.p2_score += score_delta

    def end_with_knock(self, knocker):
        """@type knocker: GinPlayer"""

        # first, handle invalid knocks with a penalty of the hand now being played face-up
        if knocker.hand.deadwood_count() > 10:
            if knocker == self.p1:
                self.p1_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p2)
            elif knocker == self.p2:
                self.p2_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p1)
        else:
            # next, handle a knock that is actually a gin (the AI will be dumb about this)
            if knocker.hand.deadwood_count() == 0:
                self.end_with_knock_gin(knocker)
            # finally, handle valid knocks
            else:
                self.gameover = True
                self.player_who_knocked = knocker

    def end_with_knock_gin(self, knocker):
        # first, handle invalid knocks with a penalty of the hand now being played face-up
        if knocker.hand.deadwood_count() != 0:
            if knocker == self.p1:
                self.p1_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p2)
            elif knocker == self.p2:
                self.p2_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p1)
        else:
            self.gameover = True
            self.player_who_knocked_gin = knocker

    # we offer the accepter a chance to accept an improper knock (provided they have a knock-worthy hand themselves)
    def offer_to_accept_improper_knock(self, accepter):
        assert isinstance(accepter, GinPlayer)
        if accepter.hand.deadwood_count() <= self.knocking_point:
            if accepter.accept_improper_knock():
                self.gameover = True
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
from utility import *


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

        # initial update for listeners
        self.noop_notify()

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

        logging.debug("--GAME OVER--"
                      "Final scores: "
                      "Player 1: {0}".format(self.p1_score) +
                      "Player 2: {0}".format(self.p2_score))

        # return winner
        if self.p1_score > self.p2_score:
            logging.debug("Player 1 Wins!")
            return self.p1
        elif self.p2_score > self.p1_score:
            logging.debug("Player 2 Wins!")
            return self.p2
        else:
            logging.debug("We have a tie!")
            # tie: flip a coin to determine winner
            if random.random() < 0.5:
                logging.debug("Player 1 wins the coin flip!")
                return self.p1
            else:
                logging.debug("Player 2 wins the coin flip!")
                return self.p2

    def notify_of_knock(self, knocker):
        self.player_who_knocked = knocker

    def notify_of_knock_gin(self, knocker):
        self.player_who_knocked_gin = knocker

    # implement the Observable criteria. return a list of ints representing our game state
    def organize_data(self):
        return {0: self.knocking_point,
                1: self.p1_score,
                2: self.p2_score,
                3: self.p1_matches_won,
                4: self.p2_matches_won}

    # play one game of gin
    @notify_observers_after
    def play_game(self):

        logging.debug("============== beginning new game between {0} and {1} ============".format(self.p1, self.p2))

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

        logging.debug("player 1 is dealt: {0}".format(self.p1.hand))
        logging.debug("player 2 is dealt: {0}".format(self.p2.hand))

    # alternate play between each player
    def take_turns(self):
        # beginning with p1, take turns until a valid knock/gin is called OR we have only two cards remaining
        while not self.gameover and len(self.table.deck.cards) >= 2:
            # both players get a chance to play, respecting knocks and end-of-game notifications
            for p in (self.p1, self.p2):
                # exit condition
                if not self.gameover:
                    p.take_turn()
                    self.log_gamestate()

                    # validate the knock or reset the knock state and penalize the knocker
                    if self.player_who_knocked:
                        self.process_knock(p)
                    # validate the knock_gin or penalize the knocker and reset the knock state
                    elif self.player_who_knocked_gin:
                        self.process_knock_gin(p)

    # award deadwood scoring and gin bonuses
    @notify_observers_after
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

        logging.debug("updated scores:"
                      "  player 1 score: ".format(self.p1_score) +
                      "  player 1 matches won: ".format(self.p1_matches_won) +
                      "  player 2 score: ".format(self.p2_score) +
                      "  player 2 matches won: ".format(self.p2_matches_won))

    def process_knock(self, knocker):
        """@type knocker: GinPlayer"""
        logging.debug("{0} knocked...".format(self.get_player_string(knocker)))

        # first, handle invalid knocks with a penalty of the hand now being played face-up
        if knocker.hand.deadwood_count() > 10:
            logging.debug("   the knock was improper.")
            if knocker == self.p1:
                self.p1_knocked_improperly = True
                if self.offer_to_accept_improper_knock(self.p2):
                    logging.debug("   {0} accepts the improper knock".format(self.get_player_string(knocker)))
                else:
                    logging.debug("   {0} does not accept the improper knock".format(self.get_player_string(knocker)))
            elif knocker == self.p2:
                self.p2_knocked_improperly = True
                if self.offer_to_accept_improper_knock(self.p1):
                    logging.debug("   {0} accepts the improper knock".format(self.get_player_string(knocker)))
                else:
                    logging.debug("   {0} does not accept the improper knock".format(self.get_player_string(knocker)))
        else:
            # next, handle a knock that is actually a gin (the AI will be dumb about this)
            if knocker.hand.deadwood_count() == 0:
                logging.debug("   the knock was actually a gin.")
                self.process_knock_gin(knocker)
            # finally, handle valid knocks
            else:
                self.gameover = True
                self.player_who_knocked = knocker

    def process_knock_gin(self, knocker):
        # first, handle invalid knocks with a penalty of the hand now being played face-up
        if knocker.hand.deadwood_count() != 0:
            logging.debug("   the knock_gin was improper.")
            if knocker == self.p1:
                self.p1_knocked_improperly = True
                if self.offer_to_accept_improper_knock(self.p2):
                    logging.debug("   {0} accepts the improper gin".format(self.get_player_string(knocker)))
                else:
                    logging.debug("   {0} does not accept the improper gin".format(self.get_player_string(knocker)))
            elif knocker == self.p2:
                self.p2_knocked_improperly = True
                if self.offer_to_accept_improper_knock(self.p1):
                    logging.debug("   {0} accepts the improper gin".format(self.get_player_string(knocker)))
                else:
                    logging.debug("   {0} does not accept the improper gin".format(self.get_player_string(knocker)))
        else:
            self.gameover = True
            self.player_who_knocked_gin = knocker

    # we offer the accepter a chance to accept an improper knock (provided they have a knock-worthy hand themselves)
    def offer_to_accept_improper_knock(self, accepter):
        assert isinstance(accepter, GinPlayer)
        if accepter.hand.deadwood_count() <= self.knocking_point:
            if accepter.accept_improper_knock():
                self.gameover = True
                return True
            else:
                return False
        else:
            return False

    # return a string representation for a given player
    def get_player_string(self, player):
        if player == self.p1:
            return "player 1"
        elif player == self.p2:
            return "player 2"
        else:
            raise Exception("player string requested for a player not in this match")

    def log_gamestate(self):
        logging.debug("----next turn-------")
        logging.debug("player 1 holds: {0}".format(self.p1.hand))
        logging.debug("player 2 holds: {0}".format(self.p2.hand))
        logging.debug("discard pile: {0}".format(self.table.discard_pile))
        logging.debug("deck height: {0}".format(len(self.table.deck.cards)))
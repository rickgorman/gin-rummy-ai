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
import random


class GinMatch(Observable):
    def __init__(self, player1, player2):
        """ @type p1: GinPlayer
            @type p2: GinPlayer
        """
        super(GinMatch, self).__init__()

        # rules
        self.maximum_turns = 60  # 30 discards possible, so each player discards each card twice
        self.turns_taken = 0
        self.knocking_point = 10

        # set up score board
        self.p1_score = 0
        self.p2_score = 0
        self.p1_games_won = 0
        self.p2_games_won = 0

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
        self.player_who_won_coinflip = False
        self.p1_wins_by_coinflip = 0
        self.p2_wins_by_coinflip = 0

        # coordinate knocks with each player
        self.p1.register_knock_listener(self)
        self.p1.register_knock_gin_listener(self)
        self.p2.register_knock_listener(self)
        self.p2.register_knock_gin_listener(self)

        # we have 5 interesting points to offer observers
        self.observable_width = 5

        # initial update for listeners
        self.noop_notify()

    # run the match until a winner is declared
    def run(self):
        # continue playing games until one player reaches 100
        while self.p1_score < 1 and self.p2_score < 1:
            self.play_game()

        # perform final scoring
        # - calculate game bonus
        if self.p1_score >= 100:
            self.p1_score += 100
        elif self.p2_score >= 100:
            self.p2_score += 100
        #else:
        #    raise ValueError("score must be 100+ for endgame. scores are p1:%s p2:%s" % self.p1_score, self.p2_score)

        # - calculate line bonus
        self.p1_score += 20 * self.p1_games_won
        self.p2_score += 20 * self.p2_games_won

        log_debug("\t--MATCH COMPLETE--")
        log_debug("\tFinal scores: ")
        log_debug("\tPlayer 1: {0}".format(self.p1_score))
        log_debug("\tPlayer 2: {0}".format(self.p2_score))

        winner = None
        # return winner
        if self.p1_score > self.p2_score:
            log_debug("Player 1 Wins!")
            winner = self.p1
        elif self.p2_score > self.p1_score:
            log_debug("Player 2 Wins!")
            winner = self.p2
        else:
            log_debug("We have a tie!")
            # tie: flip a coin to determine winner
            if random.random() < 0.5:
                log_debug("Player 1 wins the coin flip!")
                winner = self.p1
            else:
                log_debug("Player 2 wins the coin flip!")
                winner = self.p2

        # calculate losses
        p1_games_lost = self.p2_games_won
        p2_games_lost = self.p1_games_won

        result = {'winner': winner,
                  'p1_games_won': self.p1_games_won,
                  'p1_games_won_by_coinflip': self.p1_wins_by_coinflip,
                  'p1_games_lost': p1_games_lost,
                  'p2_games_won': self.p2_games_won,
                  'p2_games_won_by_coinflip': self.p2_wins_by_coinflip,
                  'p2_games_lost': p2_games_lost}

        return result

    def notify_of_knock(self, knocker):
        self.player_who_knocked = knocker

    def notify_of_knock_gin(self, knocker):
        self.player_who_knocked_gin = knocker

    # implement the Observable criteria. return a list of ints representing our game state
    def organize_data(self):
        return {0: self.knocking_point,
                1: self.p1_score,
                2: self.p2_score,
                3: self.p1_games_won,
                4: self.p2_games_won}

    # play one game of gin
    @notify_observers_after
    def play_game(self):

        log_debug("")
        log_debug("========================================================================================")
        log_debug("========================================================================================")
        log_debug("========================================================================================")
        log_debug("========================================================================================")
        log_debug("========================================================================================")
        log_info("\tbeginning new game between {0} and {1}".format(self.p1, self.p2))

        # clear game states
        self.gameover = False
        self.turns_taken = 0
        self.player_who_knocked_gin = False
        self.player_who_knocked = False
        self.p1_knocked_improperly = False
        self.p2_knocked_improperly = False
        self.player_who_won_coinflip = False

        # play one game
        self.deal_cards()
        self.take_turns()
        self.update_score()

        # post-game cleanup
        self.table.refresh_deck()
        self.p1.empty_hand()
        self.p2.empty_hand()

        log_debug("")
        log_debug("\tGame over")

    # deal out 11 cards to p1 and 10 cards to p2
    def deal_cards(self):
        # deal 10 cards to each player
        for i in range(10):
            self.p1.draw()
            self.p2.draw()

        # deal an 11th card to first player
        self.p1.draw()

        log_debug("")
        log_debug("\tplayer 1 is dealt: {0}".format(self.p1.hand))
        log_debug("\tplayer 2 is dealt: {0}".format(self.p2.hand))
        log_debug("")

    # alternate play between each player
    def take_turns(self):
        # beginning with p1, take turns until a valid knock/gin is called OR we have only two cards remaining
        #  OR we have taken too many turns
        while not self.gameover:
            # if we only have two cards remaining or have reached our turn limit, we coinflip for the win
            if not len(self.table.deck.cards) > 2 or not self.turns_taken < self.maximum_turns:
                self.end_game_with_coinflip()
            else:
                # both players get a chance to play, respecting knocks and end-of-game notifications
                for p in (self.p1, self.p2):
                    # exit condition
                    if not self.gameover:
                        log_debug(
                            "\tTurn {0}. It is {1}'s turn:".format(self.turns_taken + 1, self.get_player_string(p)))
                        p.take_turn()

                        # validate the knock or reset the knock state and penalize the knocker
                        if self.player_who_knocked:
                            self.process_knock(p)
                        # validate the knock_gin or penalize the knocker and reset the knock state
                        elif self.player_who_knocked_gin:
                            self.process_knock_gin(p)

                        self.log_gamestate()

                        # count turns
                        self.turns_taken += 1

    def end_game_with_coinflip(self):
        self.gameover = True

        if random.random() < 0.5:
            log_info("\t\tPlayer 1 wins the game by coin flip.")
            self.player_who_won_coinflip = self.p1
        else:
            log_info("\t\tPlayer 2 wins the game by coin flip.")
            self.player_who_won_coinflip = self.p2

    # award deadwood scoring and gin bonuses
    @notify_observers_after
    def update_score(self):
        score_delta = 0

        # first, handle any games won by coin flips by awarding 25 points
        if self.player_who_won_coinflip == self.p1:
            self.p1_score += 25
            self.p1_games_won += 1
            self.p1_wins_by_coinflip += 1
        elif self.player_who_won_coinflip == self.p2:
            self.p2_score += 25
            self.p2_games_won += 1
            self.p2_wins_by_coinflip += 1
        # handle non-coinflip wins
        else:
            # track the 'defender' of the knock/gin
            if self.p1 == self.player_who_knocked or self.p1 == self.player_who_knocked_gin:
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
                    self.p1_games_won += 1
                elif knocker == self.p2:
                    self.p2_score += score_delta
                    self.p2_games_won += 1

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
                        self.p2_games_won += 1
                    elif knocker == self.p2:
                        self.p1_score += score_delta
                        self.p1_games_won += 1
                # regular knocks
                else:
                    if knocker == self.p1:
                        self.p1_score += score_delta
                        self.p1_games_won += 1
                    elif knocker == self.p2:
                        self.p2_score += score_delta
                        self.p2_games_won += 1

        assert self.p1_games_won >= self.p1_wins_by_coinflip, "bad p1 score"
        assert self.p2_games_won >= self.p2_wins_by_coinflip, "bad p2 score"

        log_debug("\t\tEnd-of-game scores:")
        log_debug("\t\t  player 1 score: {0}".format(self.p1_score))
        log_debug("\t\t  player 1 matches won: {0}".format(self.p1_games_won))
        log_debug("\t\t  player 2 score: {0}".format(self.p2_score))
        log_debug("\t\t  player 2 matches won: {0}".format(self.p2_games_won))

    def process_knock(self, knocker):
        """@type knocker: GinPlayer"""
        log_debug("\tValidating knock...".format(self.get_player_string(knocker)))

        # first, handle invalid knocks with a penalty of the hand now being played face-up
        if knocker.hand.deadwood_count() > self.knocking_point:
            log_debug("\t\tthe knock was improper.")
            if knocker == self.p1:
                self.p1_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p2)
            elif knocker == self.p2:
                self.p2_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p1)
        else:
            # next, handle a knock that is actually a gin (the AI will be dumb about this)
            if knocker.hand.deadwood_count() == 0:
                log_debug("\t\tthe knock was actually a gin.")
                self.player_who_knocked = False
                self.player_who_knocked_gin = True
                self.process_knock_gin(knocker)
            # finally, handle valid knocks
            else:
                self.gameover = True
                self.player_who_knocked = knocker
                log_info("\t\tGame won by knock by {0}".format(self.get_player_string(knocker)))

    def process_knock_gin(self, knocker):
        # first, handle invalid knocks with a penalty of the hand now being played face-up
        if knocker.hand.deadwood_count() != 0:
            if knocker == self.p1:
                self.p1_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p2)
            elif knocker == self.p2:
                self.p2_knocked_improperly = True
                self.offer_to_accept_improper_knock(self.p1)
        # handle valid knock_gins
        else:
            self.gameover = True
            self.player_who_knocked_gin = knocker
            log_info("\t\tGame won by knock by {0}".format(self.get_player_string(knocker)))

    # we offer the accepter a chance to accept an improper knock (provided they have a knock-worthy hand themselves)
    def offer_to_accept_improper_knock(self, accepter):
        assert isinstance(accepter, GinPlayer)
        log_debug("\t\tthe knock_gin was improper.")

        if accepter.hand.deadwood_count() <= self.knocking_point:
            log_debug("\t\t\t{0} is eligible for the option".format(self.get_player_string(accepter)))
            if accepter.accept_improper_knock():
                log_info("\t\t\t{0} accepts the invalid knock".format(self.get_player_string(accepter)))
                self.gameover = True
                return True
            else:
                log_debug("\t\t\t{0} does not accept the invalid knock".format(self.get_player_string(accepter)))
                return False
        else:
            log_debug("\t\t\t{0} is not eligible for the option to accept".format(self.get_player_string(accepter)))
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
        if enable_logging_debug is False:
            log_debug("")
            log_debug("\t+---next turn---------------------------------------------")
            log_debug("\t| player 1 holds: {0} \tdeadwood: {1}".format(self.p1.hand, self.p1.hand.deadwood_count()))
            log_debug("\t| player 2 holds: {0} \tdeadwood: {1}".format(self.p2.hand, self.p2.hand.deadwood_count()))
            log_debug("\t| deck height: {0}  next_card: {1}  \n\t| discard pile: {2}".format(len(self.table.deck.cards),
                                                                                       self.table.deck.cards[-1],
                                                                           self.table.discard_pile))
            log_debug("\t|")
            log_debug("\t+----------------------------------------------------------")
            log_debug("")
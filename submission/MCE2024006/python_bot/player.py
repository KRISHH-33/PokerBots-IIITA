'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        #my_bounty = round_state.bounties[active]  # your current bounty rank
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        
        my_bounty_hit = terminal_state.bounty_hits[active]  # True if you hit bounty
        opponent_bounty_hit = terminal_state.bounty_hits[1-active] # True if opponent hit bounty
        bounty_rank = previous_state.bounties[active]  # your bounty rank

        # The following is a demonstration of accessing illegal information (will not work)
        opponent_bounty_rank = previous_state.bounties[1-active]  # attempting to grab opponent's bounty rank

        if my_bounty_hit:
            print("I hit my bounty of " + bounty_rank + "!")
        if opponent_bounty_hit:
            print("Opponent hit their bounty of " + opponent_bounty_rank + "!")

    def get_action(self, game_state, round_state, active):

        legal_actions = round_state.legal_actions()
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]

        my_pip = round_state.pips[active]
        opp_pip = round_state.pips[1-active]
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]

        continue_cost = opp_pip - my_pip
        pot = (STARTING_STACK - my_stack) + (STARTING_STACK - opp_stack)

        rank_order = "23456789TJQKA"

        def card_rank(card):
            return rank_order.index(card[0])

        r1 = card_rank(my_cards[0])
        r2 = card_rank(my_cards[1])

        strength = 0

        if r1 == r2:
            strength += 80

        if max(r1, r2) >= 11:
            strength += 30

        if abs(r1 - r2) <= 2:
            strength += 10

        if street >= 3:
            board_ranks = [card_rank(c) for c in board_cards]
            all_ranks = [r1, r2] + board_ranks

            counts = {}
            for r in all_ranks:
                counts[r] = counts.get(r, 0) + 1

            pairs = sum(1 for v in counts.values() if v == 2)
            trips = any(v == 3 for v in counts.values())

            if trips:
                strength += 70
            elif pairs >= 2:
                strength += 45
            elif pairs == 1:
                strength += 20

        pot_odds = continue_cost / (pot + 1) if continue_cost > 0 else 0

        bluff = random.random() < 0.07

        if strength >= 90 and RaiseAction in legal_actions:
            min_raise, _ = round_state.raise_bounds()
            return RaiseAction(min_raise)

        if strength >= 65:
            if RaiseAction in legal_actions and random.random() < 0.5:
                min_raise, _ = round_state.raise_bounds()
                return RaiseAction(min_raise)
            return CallAction() if continue_cost > 0 else CheckAction()

        if strength >= 45:
            if continue_cost == 0:
                return CheckAction()
            if pot_odds < 0.3:
                return CallAction()
            return FoldAction()

        if strength >= 25:
            if continue_cost == 0:
                return CheckAction()
            if pot_odds < 0.18:
                return CallAction()
            return FoldAction()

        if bluff and RaiseAction in legal_actions and pot < 60:
            min_raise, _ = round_state.raise_bounds()
            return RaiseAction(min_raise)

        if continue_cost == 0:
            return CheckAction()

        if continue_cost < 3:
            return CallAction()

        return FoldAction()

    
if __name__ == '__main__':
    run_bot(Player(), parse_args())

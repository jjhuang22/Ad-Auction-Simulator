#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index

class Armlb1bb:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)

        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        my_slot_info = self.slot_info(t, history, reserve)
        prev_round = history.round(t-1)
        utilities = []
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids) + [(self.id, 0)]
        other_bids.sort(key=lambda x: x[1])
        other_bids = other_bids[::-1]
        prev_clicks = prev_round.clicks + [0]
        # other_clicks = filter(lambda (a_id, b): a_id != self.id, zip(prev_round.occupants, prev_round.clicks))
        for ind in range(len(other_bids)):
            if ind == len(prev_clicks) - 2:
                utilities.append(prev_clicks[ind] * (self.value - reserve))
            else:
                utilities.append(prev_clicks[ind] * (self.value - other_bids[ind][1]))
        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        try:
            return info[i]
        except:
            i =  argmax_index(self.expected_utils(t, history, reserve)[:-1])
            return info[i]


    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (j, min_bid, max_bid) = self.target_slot(t, history, reserve)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids) + [0]
        # other_payments = filter(lambda (a_id, b): a_id != self.id, zip(prev_round.occupants, prev_round.per_click_payments)) + [0]
        # utilites = []
        # for (bid, pos, t) in zip(prev_round.bids, prev_round.clicks, prev_round.per_click_payments):
        #     utilities.append(pos * (self.value - bid))
        # j = argmax_index(utilities)
        if min_bid > self.value or j==0:
            bid = self.value
        elif j == len(prev_round.clicks) - 1:
            bid = self.value - float(prev_round.clicks[j])/prev_round.clicks[j-1]*float(self.value - min_bid)
        elif j > 0:
            bid = self.value - float(prev_round.clicks[j])/prev_round.clicks[j-1]*float(self.value - min_bid)
        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)



from ginhand import *
import unittest


class Helper(unittest.TestCase):

    @staticmethod
    def helper_generate_ginhand_from_card_data(cdata):
        g = GinHand()
        for c in cdata:
            g.add_card(GinCard(c[0], c[1]))
        return g

    @staticmethod
    def helper_generate_gincardgroup_from_card_data(cdata):
        cg = GinCardGroup()
        for c in cdata:
            cg.add(c[0], c[1])
        return cg

    # we pass in a control array (array of meld definitions like [(1, 'c'), (2, 'c'), (3, 'c')]) and
    # a test array of GinCardGroups. generate GinCardGroups for the control data and return true if they match.
    def compare_arrays_of_cardgroups(self, control_definitions, agcg_test):
        """
        @type agcg_test: GinCardGroup
        """

        agcg_control = []
        for meld_definition in control_definitions:
            agcg_control.append(GinCardGroup(meld_definition))

        # the number of GCG's must be the same
        if not len(agcg_control) == len(agcg_test):
            return False

        # compare each expected/generated pair by value
        for i in range(0, len(agcg_test)):
            for j in range(0, len(agcg_test[i].cards)):
                self.assertEqual(agcg_test[i].cards[j].rank, agcg_control[i].cards[j].rank)
                self.assertEqual(agcg_test[i].cards[j].suit, agcg_control[i].cards[j].suit)
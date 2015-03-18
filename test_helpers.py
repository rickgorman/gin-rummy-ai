from ginhand import *

class Helper():
    def __init__(self):
        pass

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

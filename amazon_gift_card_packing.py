#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage: edit hardcoded GIFT_CARD_TOTAL and PURCHASES array defined below.
Run as ./amazon_gift_card_packing.py
"""

from collections import defaultdict
import logging

LOG = logging.getLogger()
LOG.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
LOG.addHandler(ch)

# how much money you have to spend on your gift card
GIFT_CARD_TOTAL = 75.0

# total cost of items eligible for free shipping should add up to FREE_SHIPPING_MIN your order to qualify for free shipping
FREE_SHIPPING_MIN = 25.0
# if your order does not qualify for free shipping, tack on an additional shipping cost of NONFREE_SHIPPING_COST
NONFREE_SHIPPING_COST = 5.99
# you can set the tax for each individual item. Only set this variable to non-zero if you haven't got the tax price for each item
EFFECTIVE_TAX_PCT = 0 # 10


class Purchase(object):
    def __init__(self, name, price, tax=0.0, shipping_fee=0.0, free_shipping_qualifier=False):
        self.name = name
        self.price = price
        self.tax = tax
        self.shipping_fee = shipping_fee
        self.free_shipping_qualifier = free_shipping_qualifier
        if shipping_fee == 0 and not free_shipping_qualifier:
            LOG.warn("item {} has $0 shipping fee and doesn't qualify for free shipping. "
                "You may want to double-check that".format(name))
        elif shipping_fee > 0 and free_shipping_qualifier:
            LOG.warn("item {} qualifies for free shipping and has a shipping cost."
                "You may want to double-check that".format(name))


PURCHASES = [
    Purchase("drying mat", price=8.49, tax=1.30, free_shipping_qualifier=True),
    Purchase("hangers", price=24.99, tax=2.79, free_shipping_qualifier=True),
    Purchase("knife sharpen", price=13.99, tax=1.80, free_shipping_qualifier=True),
    Purchase("phone repair kit", price=14.99, tax=1.89, free_shipping_qualifier=True),
    Purchase("pick of destiny", price=12.50, tax=1.13, free_shipping_qualifier=True),
    Purchase("pirate flag", price=26.62, tax=2.81, shipping_fee=4.50),
    Purchase("printing paper", price=8.99, tax=1.35, free_shipping_qualifier=True),
    Purchase("radar detect power cord", price=5.99, tax=0.99, shipping_fee=4.99),
    Purchase("steel wool", price=3.31, tax=0.84, free_shipping_qualifier=True),
    Purchase("tao te ching", price=12.15, tax=1.45, shipping_fee=3.99, free_shipping_qualifier=False)
]

def add_purchases(purchase_dict, tax_pct=EFFECTIVE_TAX_PCT):
    value = 0
    for purchase in purchase_dict.values():
        if EFFECTIVE_TAX_PCT != 0 and purchase.tax != 0:
            LOG.warn("purchase {} has non-zero tax value!".format(purchase.name))
        value += purchase.price + purchase.tax
    value *= (100.0 + float(tax_pct)) / 100.0
    for purchase in purchase_dict.values():
        value += purchase.shipping_fee

    return value

def free_shipping_eligible_total(purchase_dict):
    eligible_price_total = 0
    for purchase in purchase_dict.values():
        if purchase.free_shipping_qualifier:
            eligible_price_total += purchase.price
    return eligible_price_total

def generate_combos(purchase_dict, stuff):
    best_combo = (purchase_dict, add_purchases(purchase_dict))
    if len(stuff) == 0:
        return best_combo

    for name, purchase in stuff.items():
        purchase_dict[name] = purchase
        del stuff[name]
        value = add_purchases(purchase_dict)
        if value <= GIFT_CARD_TOTAL:
            proposed_purchases, proposed_price = generate_combos(purchase_dict, stuff)
            if proposed_price > best_combo[1] and proposed_price <= GIFT_CARD_TOTAL:
                if free_shipping_eligible_total(proposed_purchases) < FREE_SHIPPING_MIN:
                    proposed_price += NONFREE_SHIPPING_COST
                if proposed_price <= GIFT_CARD_TOTAL:
                    best_combo = (dict(proposed_purchases), proposed_price)
        del purchase_dict[name]
        stuff[name] = purchase

    return best_combo


def main():
    purchase_dict = {
        purchase.name: purchase for purchase in PURCHASES
    }
    best_combo_purchases, best_combo_total = generate_combos({}, purchase_dict)

    for purchase in best_combo_purchases.values():
        print("{} = ${:.2f} (${:.2f} + ${:.2f} tax)".format(
            purchase.name, purchase.price + purchase.tax, purchase.price, purchase.tax
        ))
    print("----------\ntotal: ${:.2f}\n----------".format(best_combo_total))

if __name__ == "__main__":
    main()

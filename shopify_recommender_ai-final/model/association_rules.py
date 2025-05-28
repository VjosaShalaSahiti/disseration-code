from collections import Counter
from itertools import combinations

def apriori(transactions):
    from collections import defaultdict
    from itertools import combinations

    item_counts = defaultdict(int)
    rules = defaultdict(set)

    for transaction in transactions:
        unique_items = set(transaction)
        for item in unique_items:
            item_counts[item] += 1
        for item_pair in combinations(unique_items, 2):
            rules[item_pair[0]].add(item_pair[1])
            rules[item_pair[1]].add(item_pair[0])

    return rules

def association_based_recommendations(purchased, transactions):
    rules = apriori(transactions)
    recommendations = []
    for item in purchased:
        if item in rules:
            recommendations.append(rules[item])

    flattened = []
    for sub in recommendations:
        if isinstance(sub, (list, set, tuple)):
            flattened.extend(sub)
        else:
            flattened.append(sub)

    return list(set(flattened))


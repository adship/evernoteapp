from collections import defaultdict
from difflib import SequenceMatcher


def match_notes(left_notes, right_notes):
    """
    Pair up similar notes from left and right lists of notes.

    :param list left_notes: List of mininote Notes
    :param list right_notes: List of mininote Notes
    :return: List of pairs matching similar left and right notes
    """
    linecount = max(len(left_notes), len(right_notes))

    def make_compare_items(notes):
        return [{'text' : note.text, 'date' : note.created_time, 'line' : i}
                 for i, note in zip(range(len(notes)), notes)]

    def note_key(note):
        return note['date']

    def note_score(note1, note2):
        textscore = SequenceMatcher(None, note1['text'], note2['text']).quick_ratio()
        linescore = float(linecount - abs(note1['line'] - note2['line'])) / linecount
        return 0.95 * textscore + 0.05 * linescore

    return match_items(make_compare_items(left_notes), 
                       make_compare_items(right_notes),
                       note_key,
                       note_score)

def match_items(left_items, right_items, itemkey, itemscore):
    """
    Pair up similar items from left and right lists of items.

    :param list left_items: List of items
    :param list right_items: List of items
    :param func itemkey: Derive a key for an item
    :param func itemscore: Return value proportional to similarity of two items
    :return: List of pairs matching left item index to right item index
    """
    compare = ListComparer(left_items, right_items, itemkey, itemscore)
    right_matches = {} # right item index -> left item index

    unmatched_left_queue = range(compare.left_count)
    while len(unmatched_left_queue) > 0:
        left  = unmatched_left_queue.pop()
        
        for right in compare.best_matches(left):
            if right not in right_matches:
                right_matches[right] = left
                break
            else:
                otherleft = right_matches[right]
                if compare.score(left, right) > compare.score(otherleft, right):
                    right_matches[right] = left
                    unmatched_left_queue.append(otherleft)
                    break

    unmached_left = set(range(compare.left_count)).difference(right_matches.values())
    unmached_right = set(range(compare.right_count)).difference(right_matches.keys())
    return [(left, right) for right, left in right_matches.items()] + \
           [(None, right) for right in unmached_right] + \
           [(left, None) for left in unmached_left]

def groupby(items, keyfunc):
    """Place items into buckets based on a key function"""
    d = defaultdict(lambda: [])
    for item in items:
        d[keyfunc(item)].append(item)
    return d

class ListComparer:
    """Compare two lists of items"""

    def __init__(self, left_items, right_items, keyfunc, scorefunc):
        """
        :param list left_items: List of left items
        :param list right_items: List of right items
        :param func keyfunc: Derive a key from an item
        :param func scorefunc: Give a similarity score to two items
        """
        self.left_items = left_items
        self.right_items = right_items
        self.left_count = len(left_items)
        self.right_count = len(right_items)
        self.keyfunc = keyfunc
        self.scorefunc = scorefunc
        self.left_prefs = {}
        # right item key -> right items index
        self.right_lookup = groupby(range(self.right_count),
                                    lambda i: keyfunc(right_items[i]))

    def score(self, left_index, right_index):
        """
        Get a similarity score for two items.

        :param int left_index: Index of left item
        :param int right_index: Index of right item
        :returns: Number proportional to similarity of items
        """
        return self.scorefunc(self.left_items[left_index],
                              self.right_items[right_index])

    def best_matches(self, left_index):
        """
        Get iterator for this left item's closest matching right items.

        :param int left_index: Index of left items
        :returns: Iterator of right item indexes
        """
        if left_index not in self.left_prefs:
            # sort matches and store an iterator
            try:
                right_items = self.right_lookup[self.keyfunc(self.left_items[left_index])]
                right_score = lambda right_index: self.scorefunc(self.left_items[left_index], self.right_items[right_index])
                order = sorted(right_items, key = right_score, reverse = True)
            except KeyError as e:
                order = []

            self.left_prefs[left_index] = iter(order)
        return self.left_prefs[left_index]

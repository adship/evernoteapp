import re


def diff_notes(left_notes, right_notes):
    """
    Correlate left and right set of notes according to a heuristic.

    :param left_notes: List of strings
    :param right_notes: List of strings
    :return: Array of pairs correlating left note index to right note index
    """
    return stable_match(SimilarityTable(left_notes, right_notes, note_similarity))

def note_similarity(note1, note2):
    """Return value between 0 and 1 for low to high similarity"""
    getwords = lambda line: set(map(str.lower, re.split(r"\s", line)))
    words1 = getwords(note1.text)
    words2 = getwords(note2.text)
    return 2 * len(words1.intersection(words2)) / float(len(words1) + len(words2))
    
def stable_match(items):
    """
    Use stable marriage algorithm to match left and right items.

    :param items: SimilarityTable for items
    :return: Array of pairs correlating left item index to right item index
    """
    left_unmatched = list(reversed(range(items.left_count)))
    right_matches = {}

    while len(left_unmatched) > 0:
        left = left_unmatched.pop()
        for right in items.matches(left):
            if right not in right_matches:
                right_matches[right] = left
                break
            elif items.compare(left, right) > items.compare(right_matches[right], right):
                left_unmatched.append(right_matches[right])
                right_matches[right] = left
                break

    unmached_left = set(range(items.left_count)).difference(right_matches.values())
    unmached_right = set(range(items.right_count)).difference(right_matches.keys())
    return sorted([(left, right) for right, left in right_matches.items()] +\
                  [(left, None) for left in unmached_left] +\
                  [(None, right) for right in unmached_right])


class SimilarityTable:
    """Compute similarity between two lists of items"""

    def __init__(self, left_items, right_items, compare_items):
        """
        :param left_items: First list of items
        :param right_items: Second list of items
        :param compare_items: Function to compare items, returns value 
                              proportional to similarity of items
        """
        self.left_items = left_items
        self.right_items = right_items
        self.sort_cache = {}
        self.left_count = len(left_items)
        self.right_count = len(right_items)
        self.compare_items = compare_items

    def compare(self, left, right):
        """
        Get similarity between items

        :param left: Left item index
        :param right: Right item index
        :return: 
        """
        return self.compare_items(self.left_items[left], self.right_items[right])

    def matches(self, left):
        """
        Get similar right items for a left item

        :param left: Left item index
        :returns: Right item index iterator (descending similarity)
        """
        def yield_cache():
            for right in self.sort_cache[left]:
                yield right

        def yield_compute():
            first_match = self.__find_exact_match(left)
            if first_match != None:
                yield first_match 

            self.sort_cache[left] = self.__full_compare(left)
            for right in self.sort_cache[left]:
                if right != first_match:
                    yield right

        if left in self.sort_cache:
            return yield_cache()
        else:
            return yield_compute()

    def __find_exact_match(self, left):
        item = self.left_items[left]
        delta = abs(len(self.left_items) - len(self.right_items))
        for right in range(left - delta, left + 1 + delta):
            if right >= 0 and right < len(self.right_items) and self.right_items[right] == item:
                return right
        try:
            return self.right_items.index(item)
        except ValueError:
            return None

    def __full_compare(self, left):
        indexsort = lambda array: sorted(range(len(array)), key = lambda i: -array[i])
        item = self.left_items[left]
        return indexsort([self.compare_items(item, other) for other in self.right_items])

from typing import Dict, List, Iterable
from itertools import zip_longest


def merge_iterable_values_under_key(*, iterable: Iterable, filter_key: str) -> str:
    """
    Function serves as a integrity check. Returns values under given key merged, for example:
    [{"text": "Random text "},
     {
         "type": "link",
         "url": ". .",
         "children": [
             {"text": "that continues within the link", "font-size": 12}
         ]
     }] -> 'Random text that continues within the link'
    """

    def _walk_tree(input_iterable, filter_key=filter_key):
        if isinstance(input_iterable, list):
            for elem in input_iterable:
                yield from _walk_tree(elem)
        elif isinstance(input_iterable, dict):
            for key, value in input_iterable.items():
                if isinstance(value, str):
                    if key == filter_key:
                        yield value
                else:
                    yield from _walk_tree(value)

    return ''.join([*_walk_tree(iterable)])


def group_nodes_by_matching_string_values(*, base: Iterable, modified: Iterable, filter_key="text"):
    """
    Given list of nodes (dict), groups them based on values of given str key; concatenated value
    is to match value found in comparison base node.
    """
    base_iter = iter(base)
    modified_iter = iter(modified)
    grouped = []
    while 1:
        try:
            to_match, matching = next(base_iter), next(modified_iter)
            target_str, matching_str = to_match[filter_key], matching[filter_key]
            group = [matching]
            while matching_str != target_str:
                matching = next(modified_iter)
                group.append(matching)
                matching_str += matching[filter_key]
            grouped.append(group)
        except StopIteration:
            return grouped


def trim_two_iterables_from_common_values(*, base: Iterable, modified: Iterable):
    """
    Given two iterables trims them left and right from common values.
    For example: ["a","b","d","c","e","f"], ["a", "b", "c", "c", "d", "f", "f", "f"] ->
    ["d", "c", "e"], ["c", "c", "d", "f", "f"]

    """

    def _drop_until_different(iterable1, iterable2):
        index = 0
        mismatch = False
        for elem_in_1, elem_in_2 in zip(iterable1, iterable2):
            if elem_in_1 != elem_in_2:
                mismatch = True
                break
            index += 1
        return (iterable1[index:], iterable2[index:]) if mismatch else (iterable1[:0], iterable2[:0])

    trim_left = _drop_until_different(base, modified)
    trimmed_left_1, trimmed_left_2 = trim_left
    trim_right = _drop_until_different([*reversed(trimmed_left_1)], [*reversed(trimmed_left_2)])
    trimmed_1, trimmed_2 = trim_right
    return [*reversed(trimmed_1)], [*reversed(trimmed_2)]


def get_nodes_with_given_key(iterable: Iterable, filter_key: str = "text") -> List:
    """
    Yields nodes containing given key.
    """

    def _walk_tree(input_iterable, filter_key=filter_key):
        if isinstance(input_iterable, list):
            for elem in input_iterable:
                yield from _walk_tree(elem)
        elif isinstance(input_iterable, dict):
            if filter_key in input_iterable:
                yield input_iterable
            else:
                for value in input_iterable.values():
                    yield from _walk_tree(value)

    return [*_walk_tree(iterable)]


def remove_nodes_with_given_key(*, iterable: Iterable, filter_key: str = "text") -> Iterable:
    """
    Deletes nodes with given key from nested iterable. Example, "text" as filter key:
    [{"text": "Random text "},
     {
         "type": "link",
         "url": ". .",
         "children": [
             {"text": "that continues within the link", "font-size": 12}
         ]
     }] ->
     [{"type": "link",
         "url": ". .",
         "children": []
        }]
    """

    def _walk_tree(input_iterable, filter_key=filter_key):
        if isinstance(input_iterable, list):
            for elem in input_iterable[:]:
                if filter_key in elem:
                    input_iterable.remove(elem)
                else:
                    _walk_tree(elem)
        elif isinstance(input_iterable, dict):
            for value in input_iterable.values():
                _walk_tree(value)

    _walk_tree(iterable)
    return iterable

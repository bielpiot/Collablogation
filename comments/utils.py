from typing import Dict, List
from jsondiff import insert, delete, replace, diff as jdiff


def merge_json_values_under_key(json: Dict, filter_key: str) -> str:
    """
    returns values merged by key from json
    """

    def _walk_json_tree(input_json, filter_key=filter_key):
        if isinstance(input_json, list):
            for elem in input_json:
                yield from _walk_json_tree(elem)
        elif isinstance(input_json, dict):
            for key, value in input_json.items():
                if isinstance(value, str):
                    if key == filter_key:
                        yield value
                else:
                    yield from _walk_json_tree(value)

    return ''.join([*_walk_json_tree(json)])


def get_all_keys_from_nested_json(json: dict) -> List:
    """
    returns set of all keys in json
    """

    def _walk_json_tree(input_json):
        if isinstance(input_json, list):
            for elem in input_json:
                yield from _walk_json_tree(elem)
        elif isinstance(input_json, dict):
            for key, value in input_json.items():
                if isinstance(value, (str, bool)):
                    yield key
                else:
                    yield from _walk_json_tree(value)

    return [*_walk_json_tree(json)]


def compare_two_json_arrays(base, modified, thread_id):
    """
    record changes introduced to json compared to input base file
    1. raw text not changed
    2. no new attributes - set of attributes remain the same
    3. new nodes introduced by text nodes separation - can only have adjacent nodes attributes
    4. only new attributes are thread_it: true
    5. no deletion
    6. inserts contain exclusively text-based nodes (text + thread_id + other attributes copied)
    """
    diff = jdiff(base, modified)
    text_base = merge_json_values_under_key(base, "text")
    text_modified = merge_json_values_under_key(modified, "text")

    condition1 = text_base == text_modified
    condition2 = delete not in diff
    condition3 = insert in diff or (len(diff) == 1 and f"thread_{thread_id}" in diff[
        0])  # if no insert then diff is always {o: {"thread_":True}}
    condition4 = 4  # inserts contains 'text' and 'thread_' + copied attrs


def group_nodes_by_matching_values(base, modified, key="text"):
    base_iter = iter(base)
    modified_iter = iter(modified)
    grouped = []
    while 1:
        try:
            to_match, matching = next(base_iter), next(modified_iter)
            target_str, matching_str = to_match[key], matching[key]
            group = [matching]
            while matching_str != target_str:
                matching = next(matching)
                group.append(matching)
                matching_str += matching[key]
            grouped.append(group)
        except StopIteration:
            return grouped


def flatten_json(json) -> List[Dict]:
    """
    returns list of dicts, in-line, children disregarded
    """

    def _walk_tree_and(input_json):
        if isinstance(input_json, list):
            for elem in input_json:
                yield from _walk_tree_and(elem)
        elif isinstance(input_json, dict):
            for key, value in input_json.items():
                if isinstance(value, (list, dict)):
                    yield 'start of nest'
                    yield from _walk_tree_and(value)
                    yield 'end of nest'
                else:
                    yield {key: value}
        else:
            return

    return [*_walk_tree_and(json)]


def get_nodes_with_given_key(json, key="text", nest="children"):
    def _walk_tree(input_json, key=key, nest=nest):
        if isinstance(input_json, list):
            for elem in input_json:
                yield from _walk_tree(elem)
        elif isinstance(input_json, dict):
            if key in input_json:
                yield input_json
            elif nest in input_json:
                yield from _walk_tree(input_json[nest])

    return [*_walk_tree(json)]

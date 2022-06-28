from ..utils import (merge_iterable_values_under_key,
                     group_nodes_by_matching_string_values,
                     trim_two_iterables_from_common_values,
                     get_nodes_with_given_key,
                     remove_nodes_with_given_key)
from django.test import TestCase

nested_iterable = [
    {"text": "Let's start!", "bold": True, "font-size": 12},
    {"type": "paragraph",
     "children": [
         {"text": " This is the first testing node. "},
         {"type": "link",
          "url": ". .",
          "children": [
              {"text": "And this is the second. Within link.", "italic": True}
          ]}
     ]},
    {"text": " And also some random text at the end."}
]

raw_text = "Let's start! This is the first testing node." \
           " And this is the second. Within link. And also some random text at the end."

text_nodes = [{"text": "Let's start!", "bold": True, "font-size": 12}, {"text": " This is the first testing node. "},
              {"text": "And this is the second. Within link.", "italic": True},
              {"text": " And also some random text at the end."}]

witout_text_nodes = [{"type": "paragraph", "children": [{"type": "link", "url": ". .", "children": []}]}]

nodes_before_split = [{"text": "Some starting sentence.", "bold": True},
                      {"text": " And a following text.", "thread_1": True},
                      {"text": " How are you doing, dear coder?"},
                      {"text": " Are you not entertained?", "code": True}]

nodes_after_split = [{"text": "Some starting", "bold": True},
                     {"text": " sentence.", "bold": True, "thread_2": True},
                     {"text": " And a following text.", "thread_1": True, "thread_2": True},
                     {"text": " How are you doing, dear coder?", "thread_2": True},
                     {"text": " Are you not ", "thread_2": True, "code": True},
                     {"text": "entertained?", "code": True}]

expected_groups = [
    [{"text": "Some starting", "bold": True}, {"text": " sentence.", "bold": True, "thread_2": True}],
    [{"text": " And a following text.", "thread_1": True, "thread_2": True}],
    [{"text": " How are you doing, dear coder?", "thread_2": True}],
    [{"text": " Are you not ", "thread_2": True, "code": True}, {"text": "entertained?", "code": True}]
]

grps = [
    [{'text': 'Some starting', 'bold': True}, {'text': ' sentence.', 'bold': True, 'thread_2': True}],
    [{'text': ' And a following text.', 'thread_1': True, 'thread_2': True}],
    [{'text': ' How are you doing, dear coder?', 'thread_2': True}],
    [{'text': ' Are you not ', 'thread_2': True, 'code': True}, {'text': 'entertained?', 'code': True}]]

trim_sets = ([[1, 2, 3, 4], [5, 6, 7, 8, 9]],
             [[1, 2, 3, 4], [1, 6, 7, 8, 9]],
             [[1, 2, 3, 4, 5], [6, 7, 8, 5]],
             [[1, 2, 3, 4, 8], [1, 2, 7, 8]],
             [[1, 2, 3, 4], [1, 2, 3, 4]])

trim_results = (([1, 2, 3, 4], [5, 6, 7, 8, 9]),
                ([2, 3, 4], [6, 7, 8, 9]),
                ([1, 2, 3, 4], [6, 7, 8]),
                ([3, 4], [7]),
                ([], []))


class TestUtils(TestCase):

    def test_merge_iterable_values_under_key(self):
        self.assertEqual(merge_iterable_values_under_key(iterable=nested_iterable, filter_key="text"), raw_text)

    def test_get_nodes_with_given_key(self):
        self.assertEqual(get_nodes_with_given_key(iterable=nested_iterable, filter_key="text"), text_nodes)

    def test_trim_two_iterables_from_common_values(self):
        for to_be_trimmed, expected_result in zip(trim_sets, trim_results):
            self.assertEqual(trim_two_iterables_from_common_values(base=to_be_trimmed[0],
                                                                   modified=to_be_trimmed[1]),
                             expected_result)

    def test_remove_nodes_with_given_key(self):
        self.assertEqual(remove_nodes_with_given_key(iterable=nested_iterable, filter_key="text"), witout_text_nodes)

    def test_group_nodes_by_matching_string_values(self):
        self.assertEqual(group_nodes_by_matching_string_values(base=nodes_before_split,
                                                               modified=nodes_after_split,
                                                               filter_key="text"),
                         expected_groups)

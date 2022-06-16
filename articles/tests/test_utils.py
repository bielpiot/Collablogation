from ..utils import merge_json_text, compare_two_json_arrays

json1 = [
    {"text": "This text has "},
    {
        "type": "link",
        "url": ". .",
        "children": [
            {"text": "link and comments"}
        ]
    }
]

json2 = [
    {"text": "This text "},
    {"text": "has", "thread_1": true},
    {
        "type": "link",
        "url": ". .",
        "children": [
            {"text": "link", "thread_1": true},
            {"text": " and comments"},
        ]
    }
]

import copy
import unittest
from datawinners.blue.rules.remove_rule import _check_and_remove_field_from_submission


class TestRemoveRule(unittest.TestCase):
    def test_should_update_submission_with_removed_field(self):
        submission_values = {
            "text2": "Natchu",
             "repeat_inner_1": [{
                 "text1": "Blue",
                 "number2": "3",
                 "number3": "4"
             },
                 {
                     "text1": "Green",
                     "number2": "5",
                     "number3": "6"
                 }],
             "group_1": [{
                 "text3": "Yellow",
                 "number4": "7",
                 "number5": "8"
             }],
             "number1": "10",
             "group_outer": [{
                 "text12": "natchu",
                 "group_inner": [{
                     "number12": "3",
                     "group_inner_1": [{
                         "group_inner2": [{
                             "school": "sch1",
                             "like": "yes"
                         }],
                         "text11": "blue"
                     }],
                     "number13": "1"
                 }],
                 "number11": "2"
             }]
        }

        updated_with_inner_nested_field_removed = {
            "text2": "Natchu",
            "repeat_inner_1": [{
                "text1": "Blue",
                "number2": "3",
                "number3": "4"
            },
                {
                    "text1": "Green",
                    "number2": "5",
                    "number3": "6"
                }],
            "group_1": [{
                "text3": "Yellow",
                "number4": "7",
                "number5": "8"
            }],
            "number1": "10",
            "group_outer": [{
                "text12": "natchu",
                "group_inner": [{
                    "number12": "3",
                    "group_inner_1": [{
                        "group_inner2": [{
                            "school": "sch1"
                        }],
                        "text11": "blue"
                    }],
                    "number13": "1"
                }],
                "number11": "2"
            }]
        }

        updated_with_field_removed = {
            "repeat_inner_1": [{
                "text1": "Blue",
                "number2": "3",
                "number3": "4"
            },
                {
                    "text1": "Green",
                    "number2": "5",
                    "number3": "6"
                }],
            "group_1": [{
                "text3": "Yellow",
                "number4": "7",
                "number5": "8"
            }],
            "number1": "10",
            "group_outer": [{
                "text12": "natchu",
                "group_inner": [{
                    "number12": "3",
                    "group_inner_1": [{
                        "group_inner2": [{
                            "school": "sch1",
                            "like": "yes"
                        }],
                        "text11": "blue"
                    }],
                    "number13": "1"
                }],
                "number11": "2"
            }]
        }

        updated_with_repeat_field_removed = {
            "text2": "Natchu",
            "repeat_inner_1": [{
                "text1": "Blue",
                "number3": "4"
            },
                {
                    "text1": "Green",
                    "number3": "6"
                }],
            "group_1": [{
                "text3": "Yellow",
                "number4": "7",
                "number5": "8"
            }],
            "number1": "10",
            "group_outer": [{
                "text12": "natchu",
                "group_inner": [{
                    "number12": "3",
                    "group_inner_1": [{
                        "group_inner2": [{
                            "school": "sch1",
                            "like": "yes"
                        }],
                        "text11": "blue"
                    }],
                    "number13": "1"
                }],
                "number11": "2"
            }]
        }

        updated_with_outer_field_removed = {
            "text2": "Natchu",
            "repeat_inner_1": [{
                "text1": "Blue",
                "number2": "3",
                "number3": "4"
            },
                {
                    "text1": "Green",
                    "number2": "5",
                    "number3": "6"
                }],
            "group_1": [{
                "text3": "Yellow",
                "number4": "7",
                "number5": "8"
            }],
            "number1": "10",
            "group_outer": [{
                "group_inner": [{
                    "number12": "3",
                    "group_inner_1": [{
                        "group_inner2": [{
                            "school": "sch1",
                            "like": "yes"
                        }],
                        "text11": "blue"
                    }],
                    "number13": "1"
                }],
                "number11": "2"
            }]
        }
        submission = copy.deepcopy(submission_values)
        _check_and_remove_field_from_submission(submission, "like")
        self.assertEqual(submission, updated_with_inner_nested_field_removed)

        submission = copy.deepcopy(submission_values)
        _check_and_remove_field_from_submission(submission, "text2")
        self.assertEqual(submission, updated_with_field_removed)

        submission = copy.deepcopy(submission_values)
        _check_and_remove_field_from_submission(submission, "number2")
        self.assertEqual(submission, updated_with_repeat_field_removed)

        submission = copy.deepcopy(submission_values)
        _check_and_remove_field_from_submission(submission, "text12")
        self.assertEqual(submission, updated_with_outer_field_removed)

import unittest
from datawinners.project.helper import create_question_list
from mangrove.datastore.question import TextQuestion

class TestHelper(unittest.TestCase):
    def test_creates_question_list_from_dict(self):
        post = {"question-title[0]":"q0","question-code[0]":"qc0","question-title[1]":"q1"
                }
        q1={'question-title':"q0",'question-code':"qc0"}
        q2={'question-title':"q1"}
        q_list=create_question_list(post)
        self.assertEquals(2,len(q_list))
        self.assertIsNone(q_list[1].get("question-code"))

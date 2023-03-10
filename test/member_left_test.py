import unittest

from logging_client import get_action_type
from messages import member_left
from new_message_request import ActionType


class MemberLeaveTests(unittest.TestCase):
    def get_action_type(self):
        self.assertEqual(
            get_action_type(member_left),
            ActionType.MEMBER_LEFT
        )


if __name__ == '__main__':
    unittest.main()

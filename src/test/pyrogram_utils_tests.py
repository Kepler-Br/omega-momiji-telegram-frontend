import unittest

from pyrogram.types import User

from new_message_request import ActionType
from pyrogram_utils import get_fullname, get_action_type, get_action_related_user
from test.messages import member_left, new_member


class GetActionTypeTests(unittest.TestCase):
    def test_member_left(self):
        self.assertEqual(
            get_action_type(member_left),
            ActionType.MEMBER_LEFT
        )

    def test_new_member(self):
        self.assertEqual(
            get_action_type(new_member),
            ActionType.NEW_MEMBER
        )


class GetActionRelatedUserTests(unittest.TestCase):
    def test_member_left(self):
        expected_related_user = member_left.left_chat_member
        related_user = get_action_related_user(member_left)

        self.assertEqual(expected_related_user.username, related_user.username)
        self.assertEqual(get_fullname(expected_related_user), related_user.fullname)

    def test_new_member(self):
        expected_related_user = new_member.new_chat_members[0]
        related_user = get_action_related_user(new_member)

        self.assertEqual(expected_related_user.username, related_user.username)
        self.assertEqual(get_fullname(expected_related_user), related_user.fullname)


class GetFullNameTests(unittest.TestCase):
    def test_firstname_and_lastname_present(self):
        user = User(
            id=12345,
            first_name='Eliza',
            last_name='Elizason'
        )

        fullname = get_fullname(user)
        self.assertEqual('Eliza Elizason', fullname)

    def test_firstname_is_none(self):
        user = User(
            id=12345,
            first_name=None,
            last_name='Elizason'
        )

        fullname = get_fullname(user)
        self.assertEqual('Elizason', fullname)

    def test_lastname_is_none(self):
        user = User(
            id=12345,
            first_name='Eliza',
            last_name=None
        )

        fullname = get_fullname(user)
        self.assertEqual('Eliza', fullname)

    def test_firstname_and_lastname_are_none(self):
        user = User(
            id=12345,
            first_name=None,
            last_name=None
        )

        fullname = get_fullname(user)
        self.assertIsNone(fullname)


if __name__ == '__main__':
    unittest.main()

import unittest

from pyrogram.types import User

from src.new_message_request import ActionType, MediaType
from src.pyrogram_utils import get_fullname, get_action_type, get_action_related_user, get_media_type

from src.test.messages import member_left, new_member, new_message_picture, new_message_picture_with_caption, \
    new_message_gif, new_message_video, new_message_voice, new_message_video_note, new_message_music, \
    new_message_forwarded, new_message_reply_to_text, new_message


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


class GetMediaTypeTests(unittest.TestCase):
    def test_new_message_picture(self):
        self.assertEqual(
            get_media_type(new_message_picture),
            MediaType.PHOTO
        )

    def test_new_message_picture_with_caption(self):
        self.assertEqual(
            get_media_type(new_message_picture_with_caption),
            MediaType.PHOTO
        )

    def test_new_message_gif(self):
        self.assertEqual(
            get_media_type(new_message_gif),
            MediaType.GIF
        )

    def test_new_message_video(self):
        self.assertEqual(
            get_media_type(new_message_video),
            MediaType.VIDEO
        )

    def test_new_message_voice(self):
        self.assertEqual(
            get_media_type(new_message_voice),
            MediaType.VOICE
        )

    def test_new_message_video_note(self):
        self.assertEqual(
            get_media_type(new_message_video_note),
            MediaType.VIDEO_NOTE
        )

    def test_new_message_music(self):
        self.assertEqual(
            get_media_type(new_message_music),
            MediaType.AUDIO
        )

    def test_new_message_forwarded(self):
        self.assertIsNone(
            get_media_type(new_message_forwarded)
        )

    def test_new_message_reply_to_text(self):
        self.assertIsNone(
            get_media_type(new_message_reply_to_text)
        )

    def test_new_message(self):
        self.assertIsNone(
            get_media_type(new_message)
        )

    def test_new_member(self):
        self.assertIsNone(
            get_media_type(new_member)
        )

    def test_member_left(self):
        self.assertIsNone(
            get_media_type(member_left)
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

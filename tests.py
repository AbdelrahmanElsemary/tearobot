import unittest
import time
import os
from pathlib import Path

from bot.commands import calculate, translate
from bot.db import DBHelper
from bot.data_types import Message, User, ScheduleEntry, Announcement

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_SQL_SCRIPT = os.path.join(BASE_DIR, "db", "bot.db.sql")


class DBHelperTest(unittest.TestCase):

    def setUp(self):
        """Create/connect to development database"""
        self.SQL_SCRIPT = Path(DB_SQL_SCRIPT).read_text()  # read a PosixPath file as str
        # db connection & creation
        self.db = DBHelper(filename="test.db")
        print("connecting to db... done.")
        self.db.setup()

    def tearDown(self):
        """Drop DB tables, close connection and remove the db later"""
        self.db.destroy()

    def test_add_message(self):
        # inserting the message
        msg = Message(1, 2, 3, 4, 5, "message 1")
        self.assertTrue(self.db.add_message(msg))
        # making sure it was inserted right
        sql = "SELECT * FROM Message"
        got_msg = Message(*self.db.cur.execute(sql).fetchone())
        self.assertEqual(msg.id, got_msg.id)
        self.assertEqual(msg.update_id, got_msg.update_id)
        self.assertEqual(msg.user_id, got_msg.user_id)
        self.assertEqual(msg.chat_id, got_msg.chat_id)
        self.assertEqual(msg.date, got_msg.date)
        self.assertEqual(msg.text, got_msg.text)
        print("testing add_message... done.")

    def test_get_message(self):
        # inserting the message
        sql = "INSERT INTO Message VALUES (?, ?, ?, ?, ?, ?)"
        params = (1, 2, 3, 4, 5, "message")
        self.db.cur.execute(sql, params)
        # making sure we get it right
        msg = self.db.get_message(1)
        self.assertTrue(isinstance(msg, Message))
        self.assertEqual(msg.id, params[0])
        self.assertEqual(msg.update_id, params[1])
        self.assertEqual(msg.user_id, params[2])
        self.assertEqual(msg.chat_id, params[3])
        self.assertEqual(msg.date, params[4])
        self.assertEqual(msg.text, params[5])
        not_msg = self.db.get_message(2)
        self.assertFalse(not_msg)
        print("testing get_message... done.")

    def test_add_user(self):
        # insert new user
        user = User(70437390, False, True, "Ahmed", "Shahwan", "ash753", "en", True, 1555512911.45624,
                    1556303495.79887, "/calculate", 332324)
        self.assertTrue(self.db.add_user(user))
        # testing if it's inserted correctly
        sql = "SELECT * FROM User"
        got_user = User(*self.db.cur.execute(sql).fetchone())
        self.assertEqual(user.id, got_user.id)
        self.assertEqual(user.is_bot, got_user.is_bot)
        self.assertEqual(user.is_admin, got_user.is_admin)
        self.assertEqual(user.first_name, got_user.first_name)
        self.assertEqual(user.last_name, got_user.last_name)
        self.assertEqual(user.username, got_user.username)
        self.assertEqual(user.language_code, got_user.language_code)
        self.assertEqual(user.active, got_user.active)
        self.assertEqual(user.created, got_user.created)
        self.assertEqual(user.updated, got_user.updated)
        self.assertEqual(user.last_command, got_user.last_command)
        self.assertEqual(user.chat_id, got_user.chat_id)

    def test_get_user(self):
        # inserting user to db using sql
        sql = "INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        params = (70437390, False, True, "Ahmed", "Shahwan", "ash753", "en", True, 1555512911.45624,
                  1556303495.79887, "/calculate", 2345)
        self.db.cur.execute(sql, params)
        # user exists
        user = self.db.get_user(params[0])
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.id, params[0])
        self.assertEqual(user.is_bot, params[1])
        self.assertEqual(user.is_admin, params[2])
        self.assertEqual(user.first_name, params[3])
        self.assertEqual(user.last_name, params[4])
        self.assertEqual(user.username, params[5])
        self.assertEqual(user.language_code, params[6])
        self.assertEqual(user.active, params[7])
        self.assertEqual(user.created, params[8])
        self.assertEqual(user.updated, params[9])
        self.assertEqual(user.last_command, params[10])
        self.assertEqual(user.chat_id, params[11])
        # user doesn't exist
        not_user = self.db.get_user(111)
        self.assertTrue(not_user is None)

    def test_get_users(self):
        # add users using sql, then get them using the function
        # inserting users using sql
        sql = "INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        user1 = (43739, False, False, "Ahme", "Shahwa", "ash75", "en", True, 51291, 30349, "/calculate", 33)
        user2 = (4373, False, True, "Ahm", "Shahw", "ash7", "en", False, 5129, 3034, "/translate", 555)
        user3 = (437, False, False, "Ah", "Shah", "ash", "en", True, 512, 303, "/ocr_url", 556)
        self.db.cur.execute(sql, user1)
        self.db.cur.execute(sql, user2)
        self.db.cur.execute(sql, user3)

        got_users = self.db.get_users()
        self.assertTrue(isinstance(got_users, list))
        self.assertTrue(len(got_users) == 3)
        self.assertTrue(isinstance(got_users[0], User))
        self.assertTrue(isinstance(got_users[1], User))
        self.assertTrue(isinstance(got_users[2], User))

    def test_set_user_last_command(self):
        # create a user in db with tested functions
        user = User(7043739, False, False, "Ahme", "Shahwa", "ash75", "en", True, 51291, 30349, "/calculate", 5554)
        self.db.add_user(user)
        # alter user's last command
        self.assertTrue(self.db.set_user_last_command(user.id, time.time(), "/translate"))
        # test alteration success
        got_user = self.db.get_user(user.id)
        self.assertEqual("/translate", got_user.last_command)

    def test_set_user_status(self):
        # create a user
        user = User(7043739, False, False, "Ahme", "Shahwa", "ash75", "en", True, 51291, 30349, "/calculate", 5556)
        self.db.add_user(user)
        # alter user's status
        self.assertTrue(self.db.set_user_status(user.id, time.time(), False))
        # test alteration success
        got_user = self.db.get_user(user.id)
        self.assertEqual(False, got_user.active)

    def test_set_user_chat_id(self):
        # create a user without caht_id
        user = User(7043739, False, False, "Ahme", "Shahwa", "ash75", "en", True, 51291, 30349, "/calculate", None)
        self.db.add_user(user)   
        # alter user's chat_id
        new_chat_id = 3456
        self.db.set_user_chat_id(user.id, time.time(), new_chat_id)
        # test alternation
        got_user = self.db.get_user(user.id)
        self.assertEqual(got_user.chat_id, new_chat_id)

    def test_get_schedule(self):
        # create schedule entries
        sql = "INSERT INTO Schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        ent1 = (1, time.time(), "Organisation", None, None, None, "Labs", None)
        ent2 = (2, time.time(), None, "Measurements", None, None, None, None)
        ent3 = (3, time.time(), None, None, None, "Communication", "DSP", None)

        self.db.cur.execute(sql, ent1)
        self.db.cur.execute(sql, ent2)
        self.db.cur.execute(sql, ent3)

        # get entries
        entries_list = self.db.get_schedule()

        self.assertTrue(isinstance(entries_list, list))
        self.assertTrue(len(entries_list) == 3)
        self.assertTrue(isinstance(entries_list[0], ScheduleEntry))
        self.assertTrue(isinstance(entries_list[1], ScheduleEntry))
        self.assertTrue(isinstance(entries_list[2], ScheduleEntry))
        print(entries_list[0], entries_list[1], entries_list[2])

    def test_add_announcement(self):
        # add announcement
        ann = Announcement(1, time.time(), "DSP Assignment 10 should be delivered tomorrow", False)
        self.assertTrue(self.db.add_announcement(ann))
        # get announcement to test
        sql = "SELECT * FROM Announcement"
        got_ann = self.db.cur.execute(sql).fetchone()
        self.assertEqual(ann.id, got_ann[0])
        self.assertEqual(ann.time, got_ann[1])
        self.assertEqual(ann.description, got_ann[2])
        self.assertEqual(ann.cancelled, got_ann[3])

    def test_get_announcements(self):
        # add some announcements
        ann1 = Announcement(1, time.time(), "DSP Assignment 10 should be delivered tomorrow", False)
        ann2 = Announcement(2, time.time(), "Communication Lecture is cancelled", False)
        ann3 = Announcement(3, time.time(), "Dr Tamer is not coming again", False)

        self.db.add_announcement(ann1)
        self.db.add_announcement(ann2)
        self.db.add_announcement(ann3)

        # get what've been added and test it
        anns = self.db.get_announcements()
        self.assertTrue(isinstance(anns, list))
        self.assertTrue(isinstance(anns[0], Announcement))
        self.assertTrue(isinstance(anns[1], Announcement))
        self.assertTrue(isinstance(anns[2], Announcement))


class CommandsTest(unittest.TestCase):

    def test_calculate_command(self):
        self.assertEqual(calculate("5*5"), "Result: 25")

    def test_translate_command(self):
        self.assertEqual(translate("Ahmed"), "أحمد")


if __name__ == "__main__":
    unittest.main()

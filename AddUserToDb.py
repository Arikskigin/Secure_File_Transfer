import sqlite3

from Diffie_Hellman import DiffieHellman
from md5hash import md5sum


def get_yes_or_no_answer(string):
    """
    prevent user from picking wrong answer

    :param string: printing to screen
    :return: yes or no string
    """
    answer = input(string)

    while answer != "yes" and answer != "no":
        answer = input("Please answer with yes or no only")
    return answer


def insert_to_data_base(name_of_user, hashed_password, public_key, private_key, cursor, login_amount):
    """
    :param login_amount:amount of times user logged in or used for key
    :param name_of_user: string
    :param hashed_password: string after hash
    :param public_key: blob to prevent dataloss
    :param private_key: string
    :param cursor: sqlite3 cursor
    :return: None
    """
    cursor.execute("INSERT OR IGNORE INTO User  (name, password, public_key, private_key,login_amount) "
                   "VALUES (?,?,?,?,?)", (name_of_user, hashed_password, public_key, private_key, login_amount))


def get_user_data(cursor):
    """

    we get info from user hash user password and save in db,also we use an instance of diffie-hellman algorithm to
    provide user with public_key and private_key for later encryption/decryption purpose
    then we save data in our sqlite3 table inside the server.

    :param cursor: cursor is for the sqlite3 database
    :return: None
    """
    d1 = DiffieHellman()
    name_of_user = input("Please enter your name user :\n ")
    password_of_user = input("Please enter your password user :\n ")
    hashed_password = md5sum(str.encode(password_of_user))

    private_key = d1.get_private_key()
    private_key = str(private_key)
    public_key = d1.gen_public_key()
    public_key = str(public_key).encode('ascii')
    login_amount = 0
    insert_to_data_base(name_of_user, hashed_password, public_key, private_key, cursor, login_amount)


def update_data_base(private_key, public_key, login_amount, cursor, nameofuser):
    """
        :param login_amount:amount of times user logged in or used for key
        :param public_key: blob to prevent dataloss
        :param private_key: string
        :param cursor: sqlite3 cursor
        :return: None
        """
    cursor.execute("UPDATE User SET public_key=?, private_key=?,login_amount=? WHERE name=?  ",
                   (public_key, private_key, login_amount, nameofuser))


class AddUserToDb:
    def __init__(self, nameofdb):
        self.name_of_db = nameofdb

    def add_user(self):
        """
            this function is for adding users into the database using sqlite3,in this function we get username and password
            we hash their password and the server saves public_key and private_key for the user.
            the private_key is stored in server so there is no data leak what so ever.
            sql injection is also prevented using the sqlite3 ? marker
            :return:
            """
        try:
            connection = sqlite3.connect(self.name_of_db)
            cursor = connection.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS User (name TEXT, password TEXT, public_key BLOB, private_key TEXT,"
                " login_amount TEXT)")
            flag = True
            while flag:
                get_user_data(cursor)

                answer = get_yes_or_no_answer("Would you like to add another user?(yes/no)")
                if answer == "yes":
                    flag = True
                else:
                    flag = False
            connection.commit()
        except sqlite3.Error as error:
            print("Failed to insert  data into sqlite table", error)
        finally:
            if (connection):
                connection.close()

    @staticmethod
    def replaceKeys(nameofuser):
        """
        replace keys if user logged in too much so it will be harder to intercept
        :return:
        """
        d1 = DiffieHellman()
        private_key = d1.get_private_key()
        private_key = str(private_key)
        public_key = d1.gen_public_key()
        public_key = str(public_key).encode('ascii')
        login_amount = 0
        try:
            connection = sqlite3.connect("User.db")
            cursor = connection.cursor()
            update_data_base(private_key, public_key, login_amount, cursor, nameofuser)
            connection.commit()
        except sqlite3.Error as error:
            print("Failed to insert  data into sqlite table", error)

        finally:
            if (connection):
                connection.close()

    @staticmethod
    def update_user_login(nameofuser):
        try:
            connection = sqlite3.connect("User.db")
            cursor = connection.cursor()
            cursor.execute("SELECT login_amount FROM User WHERE name=?",
                           (nameofuser,))
            result = cursor.fetchone()
            new_login_amount = int(result[0]) + 1
            cursor.execute("UPDATE User SET login_amount=? WHERE name=?  ",
                           (new_login_amount, nameofuser))

            connection.commit()
        except sqlite3.Error as error:
            print("Failed to insert  data into sqlite table", error)

        finally:
            if (connection):
                connection.close()
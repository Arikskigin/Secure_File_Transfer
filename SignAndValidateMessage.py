import sqlite3
import xlsxwriter
from Crypto.PublicKey import RSA
from hashlib import sha512


def insert_to_sign_db(sign_msg, signature, public_key_e, public_key_r):
    """
    :param sign_msg: hexdigest of file
    :param signature: created by hash func
    :param public_key_e: size of key(public key)
    :param public_key_r: public key
    :return:
    """
    try:
        connection = sqlite3.connect("Sign.db")
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS Sign (assignedTo BLOB, signature BLOB, pubKey_e BLOB,pubkey_d BLOB)")
        cursor.execute("INSERT OR IGNORE INTO Sign  (assignedTo,signature, pubKey_e,pubkey_d ) VALUES (?,?,?,?)",
                       (sign_msg, signature, public_key_e, public_key_r))

        connection.commit()

    except sqlite3.Error as error:
        print("Failed to insert  data into sqlite table", error)
    finally:
        if (connection):
            connection.close()


class SignAndValidateMessage:
    def __init__(self, msg):
        self.message = msg

    def sign_message(self):
        """
        this function makes hash function out of hexdigest of file then signs digitally with file hexdigest and send data
        for signature validation into db for further use
        :param msg: hexdigest of file
        :return: none

        """

        keyPair = RSA.generate(bits=1024)
        sign_msg = bytes(str(self.message), 'cp1251')
        hash = int.from_bytes(sha512(sign_msg).digest(), byteorder='big')
        signature = pow(hash, keyPair.d, keyPair.n)
        signature = str(signature).encode('ascii')
        public_key_r = str(keyPair.n).encode('ascii')
        public_key_e = str(keyPair.e).encode('ascii')
        insert_to_sign_db(sign_msg, signature, public_key_e, public_key_r)

    def validate_signeture(self):
        """
        this function validates signeture using a hash function then it makes hash comparison
        :param msg: hexdigest of file
        :return: bool
        """

        try:
            connection = sqlite3.connect("Sign.db")
            cursor = connection.cursor()
            msg_to_find = bytes(str(self.message), 'cp1251')
            cursor.execute("SELECT assignedTo,signature,pubKey_e,pubkey_d FROM Sign WHERE assignedTo=?",
                           (msg_to_find,))
            result = cursor.fetchone()

            hash = int.from_bytes(sha512(msg_to_find).digest(), byteorder='big')
            hashFromSignature = pow(int(result[1]), int(result[2]), int(result[3]))
            if hash == hashFromSignature:
                print("Signature is Valid: You can view decrypted file")
                return True
            else:
                print("Signature is Invalid: File content is deleted")
                workbook = xlsxwriter.Workbook('decrypted_customers_data.xlsx')
                workbook.close()
                return False

        except sqlite3.Error as error:
            print("Failed to insert  data into sqlite table", error)
        finally:
            if (connection):
                connection.close()

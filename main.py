import sys
from md5hash import md5sum
from Diffie_Hellman import DiffieHellman
import sqlite3
import os
from EncryptAndDecryptFile import EncryptAndDecryptFile as EaD
from FileHelp import FileHelp as FH
from AddUserToDb import AddUserToDb as AUTDb
from SignAndValidateMessage import SignAndValidateMessage as SAVM


def encrypt_customers_data(encription):
    """
    this function encrypt data using diffie-hellman shared_key in rc6 encryption algorithm,it reads data from store
    customers xlsx file and creates encrypted_costomers_data xlsx file with encrypted data of the customers
    :param encription: hashed key for encrypt
    :return: name of encrypted file
    """
    loc = FH.fix_file_checksum()
    loc_hased = FH.turn_file_to_hash(loc)
    digest = FH.md5checksum(loc_hased)
    rc6_encrypted_file = EaD(encription, loc, "encrypted_customers_data.xlsx")
    rc6_encrypted_file_name = rc6_encrypted_file.Encrypt()
    hashed_rc6_encrypted_file = EaD(encription, loc_hased, "hashed_encrypted_customers_data.xlsx")
    hashed_rc6_encrypted_file_name = hashed_rc6_encrypted_file.Encrypt()

    return rc6_encrypted_file_name, hashed_rc6_encrypted_file_name, digest


def decrypt_customers_data(encription_key, encrypted_file, hashed_encrypted_file):
    """
    we decrpt data from our encrypted file and create a new xlsx file called decrypted_customers_data whice after
    decrpytion process has all of the customers names,
    :param encription: shared_key from diffie-hellman algorithm which is the key for decryption
    :param file: name of encrypted file
    :return: None
    """
    decrypted_customers_data = EaD(encription_key, encrypted_file, "decrypted_customers_data.xlsx")
    decrypted_customers_data_name = decrypted_customers_data.Decrypt()
    hashed_decrypted_customers_data = EaD(encription_key, hashed_encrypted_file, "hashed_decrypted_customers_data.xlsx")
    hashed_decrypted_customers_data_name = hashed_decrypted_customers_data.Decrypt()
    digest2 = FH.md5checksum(hashed_decrypted_customers_data_name)
    os.remove(r'' + hashed_decrypted_customers_data_name)
    validate = SAVM(digest2)
    if validate.validate_signeture():
        print("Done")


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


def enter_system():
    """
    this function is a login method,after succsesful login there is a public key exchange between another user that is also verified that he
    is inside the system(a user aswell) then we exchange public_keys from 2 users of the system and create the shared_key from
    diffie-hellman algorithm using the other user public_key and our own private_key to get shared_key whice we encrypt data
    using rc6 algorithm with(it is the secret key).
    how do we prevent man-in-the-middle attack?
    out network exchange is only between public_keys from each user we send user_a the public_key of user_b and the
    other way around ,there is no private_key transfer/exchange whatsoever,our private key is randomlly generated then
    it is digested
    to perform a digital signiture then after the shared_key is created we hash it and compare it with the shared_key
    of the other user if they are similar we send encrpyed_file and the user,uses his shared_key to decrypt the file.
    betfore the decryption is made first we use a digital signature to authenticate the file using hash comparison

    Diffie Hellman uses a private-public key pair to establish a shared secret, typically a symmetric key.
    DH is not a symmetric algorithm – it is an asymmetric algorithm used to establish a shared secret for
    a symmetric key algorithm.
    :return:
    """
    name_of_user = input("Login ->Enter your user name :\n ")
    password_of_user = input("Please enter your password user :\n ")
    hashed_password = md5sum(str.encode(password_of_user))
    try:
        connection = sqlite3.connect("User.db")
        cursor = connection.cursor()
        cursor.execute("SELECT name,password FROM User WHERE name=? and password=?", (name_of_user, hashed_password))
        result = cursor.fetchone()
        if result:
            print("System Access Granted\n")
            answer = get_yes_or_no_answer("Would you like to view customers data?(yes/no)\n")
            if answer == "yes":
                cursor.execute("SELECT public_key,private_key,login_amount FROM User WHERE name=? and password=?",
                               (name_of_user, hashed_password))
                result = cursor.fetchone()
                if int(result[2]) >= 5:  # change user keys if overused the same keys
                    AUTDb.replaceKeys(name_of_user)
                AUTDb.update_user_login(name_of_user)
                name_of_second_user = input("select name of second user(in db) for authentication\n")
                cursor.execute("SELECT name,public_key,private_key,login_amount FROM User WHERE name=?",
                               (name_of_second_user,))
                result2 = cursor.fetchone()
                if result2:
                    if int(result2[3]) >= 5:  # change user keys if overused the same keys
                        AUTDb.replaceKeys(result2[0])
                    AUTDb.update_user_login(name_of_second_user)
                    sharedkey_user_one = DiffieHellman().gen_shared_key(int(result2[1]), int(result[1]))
                    encrypted_file, hashed_encrypted_file, signed_file_hex = encrypt_customers_data(sharedkey_user_one)
                    sign = SAVM(signed_file_hex)
                    sign.sign_message()
                    sharedkey_user_two = DiffieHellman().gen_shared_key(int(result[0]), int(result2[2]))
                    if sharedkey_user_one == sharedkey_user_two:
                        decrypt_customers_data(sharedkey_user_two, encrypted_file, hashed_encrypted_file)
                else:
                    print("User does not exist in db")
        else:
            print("Wrong information")
    except sqlite3.Error as error:
        print("Failed to insert  data into sqlite table", error)
    finally:
        if (connection):
            connection.close()


if __name__ == '__main__':

    try:
        print("Menu:")
        print("1. Add Users to DB")
        print("2. LogIn")
        choose = input("Please enter desired part: ")

        if choose == "1":
            add_users_to_db = AUTDb("User.db")
            add_users_to_db.add_user()
            sys.exit(0)
        if choose == "2":
            enter_system()
            sys.exit(0)
        raise NotImplementedError("Part does not exist")

    except Exception as err:
        print("Unexpected error occurred: " + str(err))
        sys.exit(1)

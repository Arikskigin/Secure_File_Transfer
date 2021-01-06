# Secure_File_Transfer


Course:Data Security and Cryptology

Assigment : Access to a dataset of a store customers. To grant access using encrypted Hash. Data are encrypted by algorithm RC6 algorithm. Decryption is jointly provided by two people with a key constructed by Diffie-Hellman and comparison the result using encrypted hash.

My Project in pytho code: Option to add users to db with sqlite3,each users gets private key and public key. User needs to login to system to retrieve file,Data is encrypted by Rc6 algorithm using Diffie-Hellman shared key after its being constructed by Diffie-Hellman protocol algorithm.Then i used hash function to sign signature with private key. and we compare between hashed file and decrypted hash file for signature validation. if valid person can view the file.

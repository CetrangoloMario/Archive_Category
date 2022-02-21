
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC



class Crypt_decrypt():
    

    @staticmethod
    def encrypt(ext,key):
        f = Fernet(key)
        with open("./utilities/download-document"+ext,"rb") as file:
            file_data = file.read()
        cipher = f.encrypt(file_data)
        return cipher
    
    @staticmethod
    def decrypt(cipher,key):
        salt = base64.b64decode(cipher[:24].encode("utf-8"))
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(cipher[24:].encode("utf-8"))
        plain_text_utf8 = plain_text.decode("utf-8")
        return plain_text_utf8
    

    @staticmethod
    def make_password(password, salt): #salt costante
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
            )
        return base64.urlsafe_b64encode(kdf.derive(password))



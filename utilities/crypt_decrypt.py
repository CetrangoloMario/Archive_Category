
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC



class Crypt_decrypt():
    

    @staticmethod
    def encrypt(text,key):
        f = Fernet(key)
        cipher = f.encrypt(text)
        return cipher
       
        
    
    @staticmethod
    def decrypt(cipher,key):
        f = Fernet(key)
        plain = f.decrypt(cipher)
        return plain
        
    

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



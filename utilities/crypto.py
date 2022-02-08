import pyaes, pbkdf2, binascii, os, secrets
from config import DefaultConfig

config = DefaultConfig()


class Crypto():

    def __init__(self):
        self.__key = pbkdf2.PBKDF2(config.SECRET_PASSWORD,config.SECRET_PASSWORD_SALT).read(32)
        self.__iv = config.SECRET_IV  
    
    def encrypt(self, plaintext: str):
        aes = pyaes.AESModeOfOperationCTR(self.__key, pyaes.Counter(self.__iv))
        cipher = aes.encrypt(plaintext)
        return binascii.hexlify(cipher) #Restituisce la rappresentazione esadecimale dei dati binari.
        

    def decrypt(self, ciphertext: str):
        decryt_bin = binascii.unhexlify(ciphertext) #Restituisce i dati binari rappresentati dalla stringa esadecimale hexstr 
        aes = pyaes.AESModeOfOperationCTR(self.__key, pyaes.Counter(self.__iv))
        return aes.decrypt(decryt_bin)
        


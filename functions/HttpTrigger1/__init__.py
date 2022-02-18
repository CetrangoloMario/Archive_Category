import logging
import time
from urllib.request import urlopen
import sys
import os
import base64

from Crypto.Cipher import AES

import requests
import json
import azure.functions as func



def main(req: func.HttpRequest) -> func.HttpResponse:
    
    nome_blob = req.params.get('url_blob') 
    key= req.parms.get('key')
    option = req.params.get('option') #crypto e compression o decrypt e decompression (flag 0-1)
    if not nome_blob or not option or not key:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            
            url_blob = req_body.get('url_blob')
            option = req_body.get('option')
            key= req_body.get('key')

    if option and key and url_blob:
        list_of_results= heandlerfunction(url_blob,key, option)
        if len(list_of_results)<=3:
           return func.HttpResponse(f"""{list_of_results[0]} \n{list_of_results[1]} \n 
            {list_of_results[2]}\n""")
        else:
           all_of_res =''
           for elem in list_of_results:
               all_of_res+=str(elem)
               all_of_res+='\n'
           return func.HttpResponse(all_of_res)
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
    
    
def heandlerfunction(url_blob,key, option):
    
    if option==0:
        return crypto_compression_func(url_blob,key)
    elif option==1:
        return decrypto_decompression_func(url_blob,key)
    
    return None
    
def crypto_compression_func(url_blob,key):
    
    pass
    


def decrypto_decompression_func(url_blob,key):
    
    pass


   
def encrypt(msg, passw):
    iv = 16 * b'\0'
    aes = AES.new(passw, AES.MODE_CBC, iv)
    encd = aes.encrypt(msg)
    return encd

def decrypt(secure, passw):
    iv = 16 * b'\0'
    aes = AES.new(passw, AES.MODE_CBC, iv)
    dec = aes.decrypt(secure)
    return dec



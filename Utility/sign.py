from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
import base64

def sign_data(private_key, data):
    if len(data) % 4 != 0:
         x = 4 - (len(data) % 4)
         #print(x)
         for i in range(0, x):
             data = data + "a"
    #print(data)
    #print(len(data))
    rsakey = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    #digest.update(b64decode(data + "===="))
    digest.update(base64.urlsafe_b64decode(data + "===="))
    sign = signer.sign(digest)
    return b64encode(sign)

def verify_sign(public_key, signature, data):
    if len(data) % 4 != 0:
        x = 4 - (len(data) % 4)
        for i in range(0, x):
            data = data + "a"
    rsakey = RSA.importKey(public_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    #digest.update(b64decode(data + "===="))
    digest.update(base64.urlsafe_b64decode(data + "===="))
    if signer.verify(digest, b64decode(signature)):
        return True
    return False

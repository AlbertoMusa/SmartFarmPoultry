#------------------------------------------ LIBRARY ------------------------------------------
from socketIO_client import SocketIO, LoggingNamespace
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Utility import sign
from jose import jws
import json
from Utility import errors, exdict
import threading

#------------------------------------------ GLOBAL VAR ------------------------------------------
pub_id = "a"
pri_id = "idprivato"
key = RSA.generate(1024)
deb = False #DEBUG
deb2 = True #DEBUG
session_id = " "
server_key = " "
stop_thread = True

def on_connect_response(*resp):
    print(resp) if deb else None
    if type(resp[0]) == int:
        errors.manage_error(resp[0])
    else:
        print('CONNECT RESPONSE') if deb2 else None
        print("response: ", resp[0]) if deb else None
        print("data response: ", resp[0]['data']) if deb else None
        print("sign response: ", resp[0]['sign']) if deb else None
        resp_data = json.loads(jws.verify(resp[0]['data'], pri_id, algorithms=['HS256']).decode())
        print("decrypt data response: ", resp_data) if deb else None
        print("key in data response: ", resp_data['key']) if deb else None
        if sign.verify_sign(resp_data['key'], resp[0]['sign'], resp[0]['data']):
            print("valid sign") if deb else None
            global server_key
            server_key = resp_data['key']
            req_data = {"otp": resp_data['otp']}
            print("data to send: ", req_data) if deb else None
            crypt_data = jws.sign(req_data, pri_id, algorithm='HS256')
            print("encrypt data to send: ", crypt_data) if deb else None
            sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
            print("sign of en data send: ", sign_crypt_data) if deb else None
            req2 = {"pub_id": pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
            print("send: ", req2) if deb else None
            print("CONNECT RESPONSE DONE") if deb2 else None
            socketIO.emit('connect_confirm', req2)
            socketIO.on('connect_estab', on_connect_estab)
            socketIO.wait(seconds=3)
        else:
            errors.manage_error(6)

def on_connect_estab(*resp):
    if type(resp[0]) == int:
        errors.manage_error(resp[0])
    else:
        print('CONNECT ESTAB') if deb2 else None
        print("response: ", resp[0]) if deb else None
        print("data response: ", resp[0]['data']) if deb else None
        print("sign response: ", resp[0]['sign']) if deb else None
        print("priv_id: ", pri_id) if deb else None
        resp_data = json.loads(jws.verify(resp[0]['data'], pri_id, algorithms=['HS256']).decode())
        print("decrypt data response: ", resp_data) if deb else None
        print("server key: ", server_key) if deb else None
        if sign.verify_sign(server_key, resp[0]['sign'], resp[0]['data']):
            print("valid sign") if deb else None
            global session_id
            session_id = resp_data['ses_id']
            print("ses_id: ", resp_data['ses_id']) if deb else None
            print("CONNECT ESTAB DONE") if deb2 else None
        else:
            errors.manage_error(6)

def on_samp_response(*resp):
    if type(resp[0]) == int:
        errors.manage_error(resp[0])

def on_conf_response(*resp):
    if type(resp[0]) == int:
        errors.manage_error(resp[0])

def on_disc_response(*resp):
    if type(resp[0]) == int:
        errors.manage_error(resp[0])

def on_changes(*resp):
    print('CHANGE') if deb2 else None
    print("------\nTH: ", resp, "\n------") if deb else None
    print("response: ", resp[0]) if deb else None
    print("data response: ", resp[0]['data']) if deb else None
    print("sign response: ", resp[0]['sign']) if deb else None
    resp_data = json.loads(jws.verify(resp[0]['data'], pri_id, algorithms=['HS256']).decode())
    print("decrypt data response: ", resp_data) if deb else None
    print("key in data response: ", server_key) if deb else None
    if sign.verify_sign(server_key, resp[0]['sign'], resp[0]['data']):
        # update new data
        print("valid sign") if deb else None
        req_data = {"ses_id": session_id, "time_req": resp_data['time_req']}
        print("data to send: ", req_data) if deb else None
        crypt_data = jws.sign(req_data, pri_id, algorithm='HS256')
        print("encrypt data to send: ", crypt_data) if deb else None
        sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
        print("sign of en data send: ", sign_crypt_data) if deb else None
        req2 = {"pub_id": pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
        print("send: ", req2) if deb else None
        print("CHANGE DONE") if deb2 else None
        socketIO.emit('change_confirm', req2)

def wait_changes():
    print("------\nTH-before loop\n------") if deb2 else None
    print("flag_th: ", stop_thread) if deb else None
    while stop_thread:
        print("TH-Loop: ", stop_thread) if deb2 else None
        socketIO.on('changes', on_changes)
        socketIO.wait(seconds=5)

socketIO = SocketIO('localhost', 5000)#, async_mode='eventlet')#LoggingNamespace)
req = {"pub_id": pub_id, "key": key.publickey().exportKey().decode("utf-8")}
print(key.publickey().exportKey()) if deb else None
print(key.publickey().exportKey().decode("utf-8")) if deb else None
socketIO.emit('connect_request', req)
socketIO.on('connect_response', on_connect_response)
socketIO.wait(seconds=3)

print('START THREAD') if deb2 else None
#thread = socketio.start_background_task(wait_changes)
x = threading.Thread(target=wait_changes)#, args=(1,))
x.start()

print('REQUIRE SAMPLE DICT') if deb2 else None
req = exdict.sampleDict
req['ses_id'] = session_id
print("data to send: ", req) if deb else None
crypt_data = jws.sign(req, pri_id, algorithm='HS256')
print("encrypt data to send: ", crypt_data) if deb else None
sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
print("sign of en data send: ", sign_crypt_data) if deb else None
req = {"pub_id": pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
print("send: ", req) if deb else None
socketIO.emit('sample_dict', req)
socketIO.on('samp_response', on_samp_response)
socketIO.wait(seconds=3)

print('REQUIRE CONFIGURATION DICT') if deb2 else None
req = exdict.configurationDict
req['ses_id'] = session_id
print("data to send: ", req) if deb else None
crypt_data = jws.sign(req, pri_id, algorithm='HS256')
print("encrypt data to send: ", crypt_data) if deb else None
sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
print("sign of en data send: ", sign_crypt_data) if deb else None
req = {"pub_id": pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
print("send: ", req) if deb else None
socketIO.emit('configuration_dict', req)
socketIO.on('conf_response', on_conf_response)
socketIO.wait(seconds=3)

print('DISCONNECT') if deb2 else None
req = {"ses_id": session_id}
print("data to send: ", req) if deb else None
crypt_data = jws.sign(req, pri_id, algorithm='HS256')
print("encrypt data to send: ", crypt_data) if deb else None
sign_crypt_data = sign.sign_data(key.exportKey(), crypt_data)
print("sign of en data send: ", sign_crypt_data) if deb else None
req = {"pub_id": pub_id, "data": crypt_data, "sign": sign_crypt_data.decode()}
print("send: ", req) if deb else None
socketIO.emit('discon', req)
stop_thread = False
x.join()
socketIO.on('disc_response', on_disc_response)
socketIO.wait(seconds=3)

print('FINISH') if deb2 else None



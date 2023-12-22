
# https://github.com/abhishek-bharadwaj/Authenticator/blob/485a940d83f3c0d8550f1be8e2e7e10d4570e031/Authenticator.py#L26

import time
import base64
import hashlib
import hmac
import os
import struct
import subprocess
import signal
import configparser
from sys import argv

argument = argv

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding='utf-8-sig')
login = config.get('vpn.phoenixit.ru', 'login').rstrip()
password = config.get('vpn.phoenixit.ru', 'password').rstrip()
secret = config.get('vpn.phoenixit.ru', 'secret').rstrip()

def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
    return h

def get_totp_token(secret):
    return str(get_hotp_token(secret, intervals_no=int(time.time()) // 30)).zfill(6)

second_password = get_totp_token(secret)

if "-c" in argument:
    subprocess.run('printf \'{0}\n{1}\n{2}\ny\' | /opt/cisco/anyconnect/bin/vpn -s connect vpn.phoenixit.ru'.format(login,password,second_password), shell=True)
elif "-d" in argument:
    subprocess.run('/opt/cisco/anyconnect/bin/vpn disconnect', shell=True)
else:
    subprocess.run('echo Добавьте к команде параметр: -c : запустить VPN , -d : остановить VPN ', shell=True)

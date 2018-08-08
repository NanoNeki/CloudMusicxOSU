# coding=utf-8
#  產生 AES key

import requests,yaml
import base64, os, json
from Crypto.Cipher import AES

# yaml file integrated
config_yaml_raw = """
# Custom sign key
sign_salt: salt

debug: false

redis:
  host: localhost
  port: 6379
  db:   0

# The real ip header passed by reverse proxy (Apache, Nginx etc.)
# None:       null
# Apache:     X-Forwarded-For
# Nginx:      X-Real-IP
# CloudFlare: CF-Connecting-IP
ip_header: null

# Netease Cloud Music API Key
encrypt:  
  e: >-
    010001

  n: >-
    00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615
    bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf
    695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46
    bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b
    8e289dc6935b3ece0462db0a22b8e7

  nonce: >-
    0CoJUm6Qyw8W8jud

# Google reCAPTCHA key
recaptcha: false
# 下面的東西在 recaptcha 為 false 的時候需要註解掉不然會出事
#  secret:  secret
#  sitekey: sitekey

ssl: false
"""
# Load and parse config file
config = yaml.load(config_yaml_raw)
encrypt = config['encrypt']
for k, v in encrypt.iteritems():
      encrypt[k] = v.replace(" ", '')

nonce = encrypt['nonce']
n, e = int(encrypt["n"], 16), int(encrypt["e"], 16)

def createSecretKey(size):
  return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

def rsaEncrypt(text):
  text = text[::-1]
  rs = pow(int(text.encode('hex'), 16), e, n)
  return format(rs, 'x').zfill(256)

print("Generating secretKey for current session...")
secretKey = createSecretKey(16)
encSecKey = rsaEncrypt(secretKey)

def aesEncrypt(text, secKey):
  pad = 16 - len(text) % 16
  text = text + pad * chr(pad)
  encryptor = AES.new(secKey, 2, '0102030405060708')
  ciphertext = encryptor.encrypt(text)
  ciphertext = base64.b64encode(ciphertext)
  return ciphertext

def encrypted_request(text):
  encText = aesEncrypt(aesEncrypt(text, nonce), secretKey)
  data = {
    'params': encText,
    'encSecKey': encSecKey
  }
  return data

headers = {
  'Origin': 'http://music.163.com',
  'X-Real-IP': '120.24.208.241',
  'Accept-Language': 'q=0.8,zh-CN;q=0.6,zh;q=0.2',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
  'Referer': 'http://music.163.com/',
  'Cookie': 'os=uwp;'
}

def req_netease(url, payload):
  data = encrypted_request(payload)
  r = requests.post(url, data = data, headers=headers)
  result = json.loads(r.text)
  if result['code'] != 200:
    return None
  return result

def req_netease_detail(songId):
  payload = '{"id":"%d","c":"[{\\"id\\":\\"%d\\"}]"}' % (songId, songId)
  data = req_netease('http://music.163.com/weapi/v3/song/detail?csrf_token=', payload)
  if data is None or data['songs'] is None or len(data['songs']) != 1:
    return None
  song =  data['songs'][0]
  return song

def req_netease_url(songId, rate):
  payload = '{"ids":"[%d]","br":%d,"csrf_token":""}' % (songId, rate)
  data = req_netease('http://music.163.com/weapi/song/enhance/player/url?csrf_token=', payload)
  if data is None or data['data'] is None or len(data['data']) != 1:
    return None
  
  song = data['data'][0]
  if song['code'] != 200 or song['url'] is None:
    return None
  song['url'] = song['url'].replace('http:', 'https:')
  song['url'] = song['url'].replace('m8.music', 'm7.music')
  return song

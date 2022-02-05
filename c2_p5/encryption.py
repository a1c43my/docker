#!/usr/bin/env python3
import pyAesCrypt
import io,os,sys,time

# Lets set buffer size and password
bufferSize = 1024
password = 'wearebackboys'

# Encrypt data
def encryptData(msg):
	pbdata = str.encode(msg)
	fIn = io.BytesIO(pbdata)
	fCiph = io.BytesIO()
	pyAesCrypt.encryptStream(fIn, fCiph, password, bufferSize)
	# Data to send (bytes-like)
	dataToSend = fCiph.getvalue()
	return dataToSend

# Decrypt data
def decryptData(msg):
	# Initializing ciphertext binary stream
	fullData = b''
	fCiph = io.BytesIO()
	fDec = io.BytesIO()
	# Convert to bytes, get length and seek to beginning
	fCiph = io.BytesIO(msg)
	ctlen = len(fCiph.getvalue())
	fCiph.seek(0)
	# Decrypt stream
	pyAesCrypt.decryptStream(fCiph, fDec, password, bufferSize, ctlen)
	decrypted = str(fDec.getvalue().decode())
	return decrypted

# Encrypt file
def encryptFile(password, file):
	if len(file) < 1 or len(password) < 1 or not os.path.isfile(file): return '> Enter correct file/password.\n'
	newfile = file + '.aes'
	bufferSize = 64 * 1024
	try:
		pyAesCrypt.encryptFile(file, newfile, password, bufferSize)
		return '> Encrypted: ' + newfile + '\n'
	except:
		return '> Error while encrypting, try again.\n'

# Decrypt file
def decryptFile(password, file):
	if len(file) < 1 or len(password) < 1 or not os.path.isfile(file): return '> Enter correct file/password.\n'
	try:
		newfile = os.path.splitext(file)[0]
	except: newfile = 'decrypted.' + file
	bufferSize = 64 * 1024
	try:
		pyAesCrypt.decryptFile(file, newfile, password, bufferSize)
		return '> Decrypted: ' + newfile + '\n'
	except:
		return '> Error while decrypting, try again.\n'

# Send encrypted data in multiple parts
def sendData(sock, data):
	# Check if command output requires breaking into pieces
	limitBytes = 675
	if sys.getsizeof(data) >= limitBytes:
		# Lets figure out how many messages to send
		calcmsg = int(round(sys.getsizeof(data) / limitBytes))
		# Get length of message to send
		sendlen = int(round(len(data) / calcmsg))
		# If we get a bad calcmsg because of rounding, add +1 and correct it here
		while sendlen > limitBytes:
			calcmsg += 1
			sendlen = int(round(len(data) / calcmsg))
		fixdlen = sendlen
		charpos = 0
		x = 1
		while x <= calcmsg:
			tosendmsg = data[charpos:sendlen]
			# On the last iteration, send full length of msg
			if x == calcmsg: 
				sendlen = len(data)
				tosendmsg = data[charpos:sendlen]
			else:
				sendlen += fixdlen
				charpos += fixdlen
			sock.sendall(encryptData(tosendmsg))
			x += 1
	else:
		sock.sendall(encryptData(data))

# Send file
def sendFile(sock, file):
	try:
		with open(file, 'rb') as f:
			fileData = f.read()
			# Begin sending file
			sock.sendall(fileData)
			time.sleep(4)
			sock.send('EOFX'.encode())
		f.close()
		return '> File transfer: ' + file + ' complete.\n'
	except:
		return '> Error sending file: ' + file + '.\n'
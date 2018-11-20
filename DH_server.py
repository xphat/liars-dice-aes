# Server to implement simplified Diffie-Hellman protocol
# The server waits for the client to say Hello. Once the client says hello,
# the server sends the client a public key. The client uses the public key to
# send a session key with confidentiality to the server. The server then sends
# a nonce (number used once) to the client, encrypted with the server's private
# key. The client decrypts that nonce and sends it back to server encrypted 
# with the session key. 

# Author: fokumdt 2018-11-15
# Version: 0.1

#!/usr/bin/python3

import socket
import random
import math
import hashlib
import time
import sys
import simplified_AES

def expMod(b,n,m):
    """Computes the modular exponent of a number"""
    """returns (b^n mod m)"""
    if n==0:
        return 1
    elif n%2==0:
        return expMod((b*b)%m, n/2, m)
    else:
        return(b*expMod(b,n-1,m))%m

def computePublicKey(g, p, s):
	"""Computes a node's public key."""
	"""You will need to implement this function"""
	pass

def computeSecretKey(g, p):
	"""Computes this node's secret key."""
	"""You will need to implement this function."""
	pass

def generateNonce():
    """This method returns a 16-bit random integer derived from hashing the
        current time. This is used to test for liveness"""
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))
    return int.from_bytes(hash.digest()[:2], byteorder=sys.byteorder)

# M   = message, an integer
# Pub = receiver's public key, an integer
# p   = prime number, an integer
# gen = generator, an integer
def DHencrypt(M, Pub, p, gen):
	"""Encrypts a message M given parameters above"""
	k = random.randint(1,p-1)
	return expMod(gen,k,p), M*expMod(Pub,k,p)

# C    = second part of ciphertext, an integer
# s    = first part of ciphertext, an integer
# priv = receiver's secret key, an integer
# p    = prime number, an integer
def DHdecrypt(C, s, priv, p):
	"""Decrypts a message C given parameters above"""
	return int(C/expMod(s,priv,p))

def clientHello():
	"""Generates client hello message"""
	status = "100 Hello"
	return status

def sendPublicKey(g, p, s):
	"""Sends node's public key"""
	status = "120 PubKey " + str(computePublicKey(g, p, s))
	return status

# M   = message, an integer
# Pub = receiver's public key, an integer
# p   = prime number, an integer
# gen = generator, an integer
def sendEncryptedMsg(M, Pub, p, gen):
	"""Sends encrypted message """
	y1, y2 = encryptMsg(M, Pub, p, gen)
	status = "130 Ciphertext " + str(int(y1)) +" " + str(int(y2))
	return status

def nonceVerification(nonce, decryptedNonce):
    """Verifies that the transmitted nonce matches that received
       from the client."""
    if (nonce == decryptedNonce):
        status = "150 OK"
    else:
        status = "400 Error"
    return status

def rollDice(dice, toRoll=[0,1,2,3,4]):
    """Rolls specified dice. If no dice are specified, all dice are rolled."""
    for i in toRoll:
        dice[i] = random.randint(1,6)
        
def RollDiceACK(dice):
    """Generates message with dice values"""
    strDice = ','.join([str(x) for x in dice])
    status = "205 Roll Dice ACK " + strDice
    return status

def make_bid(bid, msg):
     """This function processes messages that are read through the socket. It
    determines whether or not the bid made is valid and returns a status.
    """

    """You will need to complete this method """
    msg = msg.split(' ')
    frequency = bid[0]
    value = bid[1]

def challenge(roll, clientRoll, msg):
    print("Server roll is: " + roll)
    print("Client's roll is: " + clientRoll)
   """This function processes messages that are read through the socket. It
    receives the client's roll and shows the server's roll. It also determines
    whether or not the challenge made is valid and returns a status.
    """

    """You will need to complete this method """


# s      = socket
# msg     = initial message being processed
# state  = dictionary containing state variables
def processMsgs(s, msg, state):
    """This function processes messages that are read through the socket. It
        returns a status, which is an integer indicating whether the operation
        was successful"""
    status = -2
    gen = int(state['Gen'])				# integer generator
    prime = int(state['prime'])			# integer prime
    sKey = int(state['SecretKey'])		# secret key
    rcvrPK = int(state['RcvrPubKey'])	# receiver's public key
    nonce = int(state['Nonce'])
    bids = int(state['Bids'])           # number of bids made
    srvrDice = int(state['ServerDice'])
    clntDice = int(state['ClientDice'])
    clntDice = list(map(int,clntDice))  # Converting dice values to ints
    srvrDice = list(map(int,srvrDice))  # Converting dice values to ints
    strTest = clientHello()
    if strTest in msg and status == -2:
	print("Message received: "+ msg)
	msg = strTest
	s.sendall(bytes(msg,'utf-8'))
	status = 1
	strTest = "110 Generator:"
	if strTest in msg and status == -2:
            print("Message received: "+ msg)
            RcvdStr = msg.split(' ')
            gen = int(RcvdStr[2][0:-1])
            prime = int(RcvdStr[4])
            sKey = ## Complete this
            msg = "111 Generator and Prime Rcvd"
            s.sendall(bytes(msg, 'utf-8'))
            state['gen'] = gen
            state['prime'] = prime
            state['SecretKey'] = sKey
            status = 1
	
	strTest = "120 PubKey"
	if strTest in msg and status == -2:
            print("Message received: " + msg)
            RcvdStr = msg.split(' ')
            rcvrPK = int(RcvdStr[2])
            msg = # Complete this
            print("Message sent: " + str(msg))
            s.sendall(bytes(msg, 'utf-8'))
            state['RcvrPubKey'] = rcvrPK
            status = 1
	
	strTest = "130 Ciphertext"
	if strTest in msg and status == -2:
            print("Message received:" + str(msg))
            Pub = # Complete this
            RcvdStr = msg.split(' ')
            y1 = int(RcvdStr[2])
            clntCtxt = int(RcvdStr[3])
            dcryptedNonce = decryptMsg(clntCtxt, y1, sKey, prime)
            msg = #complete this
            s.sendall(bytes(msg, 'utf-8'))
            print("Message sent: " + msg)
            status = 0		# To terminate loop at server.

    strDiceRollResp = "200 Roll Dice"
    if strDiceRollResp in msg and status == -2:
        print("Message received: " + msg)
        rollDice(clntDice)
        msg = RollDiceACK(clntDice)
        s.sendall(bytes(msg,'utf-8'))
        state['ClientDice'] = clntDice
        status = 1
	
	# status can only be -2 if none of the other branches were followed
	if status==-2:
		print("Incoming message was not processed. \r\n Terminating")
		status = -1
	return status

def main():
	"""Driver function for the project"""
	args = sys.argv
	if len(args) != 2:
		print ("Please supply a server port.")
		sys.exit()
	HOST = ''		# Symbolic name meaning all available interfaces
	PORT = int(args[1])     # The port on which the server is listening
	if PORT < 1023 or PORT > 65535:
		print("Invalid port specified.")
		sys.exit()
	# Initializing generator, prime, secret key, and receiver's public key with
	# bogus values. The actual values will come from values read from the socket
	generator = 3
	prime = 127
	secretKey = computeSecretKey(generator, prime)
	rcvrPK = 5     # Initial value for receiver's public key
    nonce = generateNonce()
    bids = 0
    srvrDice = [random.randint(1,6), random.randint(1,6), random.randint(1,6),
            random.randint(1,6),random.randint(1,6)]
    clntDice = [random.randint(1,6), random.randint(1,6), random.randint(1,6),
            random.randint(1,6),random.randint(1,6)]
	state = {'Gen': generator, 'prime': prime, 'SecretKey': secretKey,
	 'RcvrPubKey': rcvrPK, 'Nonce': nonce, 'ServerDice': srvrDice,
	 'ClientDice': clntDice, 'Bids': bids }
	
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((HOST, PORT))
		s.listen(1)
		conn, addr = s.accept()
		with conn:
			print('Connected by', addr)
			status = 1
			while (status==1):
				msg = conn.recv(1024).decode('utf-8')
				if not msg:
					status = -1
				else:
					status = processMsgs(conn, msg, state)
			if status < 0:
				print("Invalid data received. Closing")
			conn.close()
			print("Closed connection socket")

if __name__ == "__main__":
	main()

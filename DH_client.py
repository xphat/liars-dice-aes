# Client to implement simplified Diffie-Hellman protocol
# The client says hello to the server, and the server responds with a Hello
# and its public key. The client then sends a session key encrypted with the
# server's public key. The server responds to this message with a nonce
# encrypted with the server's public key. The client decrypts the nonce
# and sends it back to the server encrypted with the session key. Next,
# the server sends the client a message with a status code. If the status code
# is "150" then the client can ask for the server to roll the dice. Otherwise,
# the client's connection to the server will be terminated.

# Author: fokumdt 2018-11-15
# Version: 0.1

#!/usr/bin/python3


import socket
import math
import random
import sys
import time
import simplified_AES
import hashlib


def expMod(b,n,m):
    """Computes the modular exponent of a number returns (b^n mod m)"""
    if n==0:
        return 1
    elif n%2==0:
        return expMod((b*b)%m, n/2, m)
    else:
        return(b*expMod(b,n-1,m))%m

def IsValidGenerator(g, p):
    """Validation of generator and prime"""
    """Write code to validate the generator and prime"""
    pass

def serverHello():
	"""Sends server hello message"""
	status = "100 Hello"
	return status

def sendGeneratorPrime(g,p):
	"""Sends server generator"""
	status = "110 Generator: " + str(g) + ", Prime: " + str(p)
	return status

def computeSecretKey(g, p):
	"""Computes this node's secret key"""
	secretKey = random.randint(int(g), int(p))
	return secretKey

def computePublicKey(g, p, s):
    """Computes a node's public key"""
    """Complete this function"""
    pass

def sendPublicKey(g, p, s):
    """Sends node's public key"""
    status = "120 PubKey " + str(computePublicKey(g, p, s))
	return status

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
def encryptMsg(M, Pub, p, gen):
	"""Encrypts a message M given parameters above"""
	k = random.randint(1,p-1)
	return expMod(gen,k,p), M*expMod(Pub,k,p)

# C    = second part of ciphertext, an integer
# s    = first part of ciphertext, an integer
# priv = sender's public key, an integer
# p    = prime number, an integer
def decryptMsg(C, s, priv, p):
	"""Decrypts a message C given parameters above"""
	return int(C/expMod(s,priv,p))

# M   = message, an integer
# Pub = receiver's public key, an integer
# p   = prime number, an integer
# gen = generator, an integer
def sendEncryptedMsg(M, Pub, p, gen):
	"""Sends encrypted message """
	y1, y2 = encryptMsg(M, Pub, p, gen)
	status = "130 Ciphertext " + str(int(y1)) +" " + str(int(y2))
	return status

def RollDice():
    """Generates message to get server to roll some or all dice."""
    toRoll = input('Roll all the dice? (y/n): ')
    toRoll = str(toRoll)
    if toRoll == 'y' or toRoll == 'Y':
        status = "200 Roll Dice"
    else:
		print("You exited the game!")
        status = ""
    return status
    
def make_bid(state):
    """This function determines whether the bid made is valid and
       returns a status.
    """
	bid  = state['lastBid']    
    bid = list(map(int,bid)) 
	status = -1
    frequency = bid[0]
    value = bid[1]
	
	face = input('Enter face value for your bid. Enter 0 to challenge: ')
    numFaces = input('Enter number of face value in your bid. Enter 0 to challenge: ')
	if (face !=0 and numFaces !=0):
		if (numFaces > frequency or face > value):
			status = 1
		else:
			print("Last bid was invalid")
			face = input('Enter face value for your bid. Enter 0 to challenge: ')
			numFaces = input('Enter number of face value in your bid. Enter 0 to challenge: ')
			status=1
	bid[0] = numFaces
	bid[1] = face
	state['lastBid'] = bid
	return status

def MakeBidMsg(state):
    """Generates message to send a bid to the server."""
	"""A bid of '300 Bid 0 0' is a challenge. """
	make_bid(state)
	bid  = state['lastBid']    
    bid = list(map(int,bid)) 
	status = "300 Bid " + str(bid[1]) + " " + str(bid[0])
    return status  

def challenge(roll, msg):
    """This function processes messages that are read through the socket. It
    receives the client's roll and shows the server's roll. It also determines
    whether or not the challenge made is valid and returns a status.
    """

    """You will need to complete this method """
    
    print('Client roll is: ' + roll)
    print('Opponent\'s roll is: ' + msg[8])



# s       = socket
# msg     = initial message being processed
def processMsgs(s, msg, state):
    """This function processes messages that are read through the socket. It
        returns a status, which is an integer indicating whether the operation
        was successful"""
        
    status = -2
	gen = int(state['gen'])				# integer generator
	prime = int(state['prime'])			# integer prime
	sKey = int(state['SecretKey'])		# secret key
	rcvrPK = int(state['RcvrPubKey'])	# receiver's public key
	nonce = int(state['nonce'])			# Number used only once
    bids = int(state['Bids'])           # bids       = number of bids made
    dice  = state['Dice']               # Dice = values of dice
    dice = list(map(int,dice))          # Converting dice values to ints

    strTest = serverHello()
    if (strTest in msg and status==-2):
        msg = ##Complete this line
        print("Message sent: " + msg)
        s.sendall(bytes(msg,'utf-8'))
        status = 1
    
    strTest = "111 Generator and Prime Rcvd"
    if (strTest in msg and status==-2):
        msg = ##Complete this line
        s.sendall(bytes(msg, 'utf-8'))
        status = 1
    
    strTest = "120 PubKey"
    if (strTest in msg and status==-2):
        RcvdStr = msg.split(' ')
        rcvrPK = int(RcvdStr[2])
        nonce = generateNonce()
        while (nonce >= prime):
            nonce = generateNonce()
        msg = ##Complete this line.
        print("Message sent: " + str(msg))
        s.sendall(bytes(msg, 'utf-8'))
        state['nonce'] = nonce
        state['RcvrPubKey'] = rcvrPK
        status = 1
    
    strTest = "130 Ciphertext"
    if (strTest in msg and status==-2):
        Pub = computePublicKey(gen, prime, sKey)
        RcvdStr = msg.split(' ')
        y1 = int(RcvdStr[2])
        srvrCtxt = int(RcvdStr[3])
        print("Ciphertext received: " + str(y1) +"," + str(srvrCtxt))
        dcryptedNonce = decryptMsg(srvrCtxt, y1, sKey, prime)
        if (abs(nonce - dcryptedNonce) == 5):
            print("Final status code: 150 OK")
        else:
            print("Final status code: 400 Error")
        status = 0		# To terminate loop at client.
    
    strDiceRoll = "205 Roll Dice ACK"
    if (strDiceRoll in msg and status==-2):
        DiceValues = msg[18:].split(',')
        if bids < 2:
            msg = MakeBidMsg(state):
            s.sendall(bytes(msg,'utf-8'))
            bids += 1
            status = 1
        else:
            status = 0
        state['Bids'] = bids
    
    strBidAck = "305 Bid ACK"
    if (strBidAck in msg and status==-2):
        print("Message received: " + msg)
        BidReceived = msg[12:].split(' ')
        if bids < 2:
            msg = MakeBidMsg(state):
            s.sendall(bytes(msg,'utf-8'))
            bids += 1
            status = 1
        else:
            status = 0
        state['Bids'] = bids
    
    strSuccess = "150 OK"
    strFailure = "400 Error"
    if ((strSuccess in msg or strFailure in msg) and status==-2):
		status = 0 # To terminate loop at client
	
	if status==-2:
		print("Incoming message was not processed. \r\n Terminating")
		status = -1
	return status                

def main():
	"""Driver function for the project"""
	args = sys.argv
	if len(args) != 3:
		print ("Please supply a server address and port.")
		sys.exit()
	serverHost = str(args[1])       # The remote host
	serverPort = int(args[2])       # The same port as used by the server
	print("\nClient of _____")
	print('''
	The dice in this program have a face value in the range 1--6.
	No error checking is done, so ensure that the bids are in the correct range.
	Follow the on-screen instructions.
	''')
	random.seed()
	dice = [random.randint(1,6), random.randint(1,6), random.randint(1,6),
            random.randint(1,6),random.randint(1,6)]
	
	while (True):
		prime = int(input('Enter a valid prime between 1024 and 65536: '))
		generator = int(input('Enter a positive integer less than the prime just entered: '))
		if (IsValidGenerator(generator, prime)): break
	nonce = generateNonce()
	# To ensure that the nonce can always be encrypted correctly.
	while (nonce >= prime):
		nonce = generateNonce()

    bids = 0
	lastBid = [0,0]
	# Bogus values that will be overwritten with values read from the socket.
	secretKey = computeSecretKey(generator, prime)
	rcvrPK = 60769
	state = {'prime': prime, 'gen': generator, 'SecretKey': secretKey,
	'RcvrPubKey': rcvrPK, 'nonce': nonce, 'LastBid': lastBid, , 'Bids': bids,
	'Dice': dice}
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((serverHost, serverPort))
	msg = serverHello()
	s.sendall(bytes(msg,'utf-8'))
	status = 1
	while (status==1):
		msg = s.recv(1024).decode('utf-8')
		if not msg:
			status = -1
		else:
			status = processMsgs(s, msg, state)
	if status < 0:
		print("Invalid data received. Closing")
	s.close()

if __name__ == "__main__":
	main()

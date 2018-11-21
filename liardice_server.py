# Server to implement simple program to get dice rolled on a server.
#  The dice values are then sent through a socket and printed on the client.
#  The user is given a choice of getting some of the dice rolled again.
# Author: fokumdt 2017-10-02
# Version: 0.1
#!/usr/bin/python3

from socket import *
import sys
import random
import simplified_AES
import time
import math
import hashlib

roll = []
clientRoll = []
cfreq = 0
cvalue = 0
global generator
global prime
global clientpubkey
global mysecretkey

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
	return expMod(g,s,p)

def computeSecretKey(g, p):
    """Computes this node's secret key."""
    secretKey = random.randint(int(g), int(p))
    return secretKey


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
	y1, y2 = DHencrypt(M, Pub, p, gen)
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

def clientHello():
    #"""Generates client hello message"""
    status = "100 Hello"
    return status

def RollDiceACK(dice):
    #"""Sends client their rolled dice"""
    strDice = ','.join([str(x) for x in dice])
    status = "205 Roll Dice ACK " + strDice
    return status

def bidACK(dice, query):
    #"""Generates message with query"""
    strDice = ','.join([str(x) for x in dice])
    if query == 'b':
        status = "305 Bid ACK " + strDice
    elif (query == 'c'):
        #read from server bid file to send correct Bid ACK Challenge Messages
        file = open("serverbid.tmp", "r") 
        allbids = file.read()
        file.close()
        bidmsg = allbids.split(' ')
        cfreq = bidmsg[0]
        cvalue = bidmsg[1]
        status = "305 Bid ACK Challenge " + strDice + " " + str(cfreq) + " " + str(cvalue)
    return status

def rollDice(dice, toRoll=[0,1,2,3,4]):
    """Rolls the dice."""
    for i in toRoll:
        dice.append(random.randint(1,6))
    return dice;

def bidPrompt(f, v):
    """Generates Question As to Whether Server Wants to Make a Bid or Call Out the LIAR."""
    toBid = input('Enter (b) to Make a Bid, Any Other Key to Call Out the LIAR: ')
    toBid = str(toBid)
    if toBid == 'b' or toBid == 'B':
        ans = [];
        value = input('Please Announce The Face Value of the Bid: ')
        frequency = input('Please Enter the Minimum Number of Dice: ')
        while (int(frequency) < int(f)):
            print("Sorry The Minimum Number of Dice Needs to Be Higher Than Last Time!")
            value = input('Please Announce The Face Value of the Bid: ')
            frequency = input('Please Enter the Minimum Number of Dice: ')
        ans.append(frequency)
        ans.append(value)
        return ans
    else:
        return -1
    
def make_bid(bid, msg):
    frequency = bid[0]
    value = bid[1]
    return "305 Bid ACK " + frequency + " " + value

def challenge(roll, clientRoll, msg):
    print("Server roll is: " + roll)
    print("Client's roll is: " + clientRoll)
    file = open("serverdice.tmp", "r") 
    alldice = file.read()
    file.close()

    file = open("serverbid.tmp", "r") 
    allbids = file.read()
    file.close()
    bidmsg = allbids.split(' ')
    cfreq = bidmsg[0]
    cvalue = bidmsg[1]
    correctcount = alldice.count(cvalue)

    if (int(correctcount) != int(cfreq)):
        print ("LIAR!! There are Actually " + str(correctcount) + " " + str(cvalue) + "'s present!")
        return "306 LOSE"
    else:
        print ("You Win!  There are Actually " + str(correctcount) + " " + str(cvalue) + "'s present!")
        return "306 WIN"


def processMsgs(s, msg):
    global generator
    global prime
    global clientpubkey
    global mysecretkey

    if (msg.startswith('100')):
        s.send(clientHello().encode())
        return 1

    if (msg.startswith('110')):
        s.send("111 Generator and Prime Rcvd".encode())
        keyarr = msg.split(' ')
        prime = int(keyarr[4])
        t = keyarr[2].split(',')
        generator = int(t[0])
        mysecretkey = computeSecretKey(generator,prime)
        print("Secret Key is " + str(mysecretkey))
        return 1

    if (msg.startswith('120')):
        keyarr = msg.split(' ')
        clientpubkey = int(keyarr[2])
        pubkey = sendPublicKey(generator, prime, mysecretkey)
        s.send(pubkey.encode())
        return 1

    if (msg.startswith('130')):
        encnonce = msg.split(' ')
        decrypnonce = DHdecrypt(int(encnonce[3]), int(encnonce[2]), mysecretkey, prime)
        decrypnonce = decrypnonce - 5
        encmsg = sendEncryptedMsg(decrypnonce, clientpubkey, prime, generator)
        s.send(encmsg.encode())
        print("Generator is : " + str(generator) + " Prime is: " + str(prime) + " My Private Key: " + str(mysecretkey) + " Client Public Key: " + str(clientpubkey))
        return 1
    

    if (msg.startswith('500')):
        s.close()
        print("Game Over!")
        exit();

    if (msg.startswith('200')):
        rollDice(roll)
        print("Server roll is: " + ','.join([str(x) for x in roll]))
        print("Waiting for Bid...")
        rollDice(clientRoll)
        alldice = ','.join([str(x) for x in roll + clientRoll])
        file = open("serverdice.tmp","w")
        file.write(alldice)
        file.close()
        s.send(RollDiceACK(clientRoll+roll).encode())
        return 1
    
    if (msg.startswith('300')):
        bidmsg = msg.split(' ')
        cfreq = bidmsg[2]
        cvalue = bidmsg[3]
        file = open("serverbid.tmp","w")
        file.write(cfreq + " " + cvalue)
        file.close()
        print("Client Bids \n" + " Die Face Value: " + cvalue + "\n Die Minimum Count: " + cfreq)
        bid = bidPrompt(cfreq, cvalue)
        if (bid == -1):
            print ("Calling Out the Liar....")
            s.send(bidACK(roll, 'c').encode())
        else:
            mbid = make_bid(bid, msg) + " " + ','.join([str(x) for x in roll])
            print ("Sending Bid to the Client....")
            s.send(mbid.encode())
        return 1

    if (msg.startswith('306')):
        gamemsg = msg.split(' ')
        if gamemsg[1] == "WIN":
            print("Server WON!")
        else:
            print("Server Lost!.. Sorry!  You are the Liar!")
        s.close()
        print("Game Over!")
        exit();
    
    pass
    

def main():
    args = sys.argv
    if len(args) != 2:
        print ("Please supply a server port.")
        sys.exit()
    HOST = ''                
    PORT = int(args[1])
    if PORT < 1023 or PORT > 65535:
        print("Invalid port specified.")
        sys.exit()
        
    print("\nServer of Rhon-Kaniel Bramwell")
    '''Specify socket parameters to use TCP'''        
    with socket(AF_INET,SOCK_STREAM) as s:
        s.bind((HOST,PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            status = 1
            while (status == 1):
                msg = conn.recv(1024).decode('utf-8')
                print(msg);
                if not msg:
                    status = -1
                else:
                    status = processMsgs(conn, msg)
            if status < 0:
                print("Invalid data received. Closing")   
            conn.close()
            print("Closed connection socket")    

if __name__ == "__main__":
    main()

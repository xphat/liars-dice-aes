# Server to implement simple program to get dice rolled on a server.
#  The dice values are then sent through a socket and printed on the client.
#  The user is given a choice of getting some of the dice rolled again.
# Author: fokumdt 2017-10-02
# Version: 0.1
#!/usr/bin/python3

from socket import *
import sys
import random

roll = []
clientRoll = []
cfreq = 0
cvalue = 0

def clientHello():
    #"""Generates client hello message"""
    status = "105 Hello"
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
    if (msg.startswith('100')):
        s.send(clientHello().encode())
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

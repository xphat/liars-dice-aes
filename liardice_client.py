# Client to implement simple program to get dice rolled on a server.
# The dice are then printed on the client and the user mkes a bid and
# poses the choice of a bid or challenge to the server.
# Author: D.Delahaye 2018-06-14
# Version: 0.1
#!/usr/bin/python3

from socket import *
import sys
import random



def serverHello():
    """Generates server hello message"""
    status = "100 Hello"
    return status

def RollDice():
    """Generates message to get server to roll some or all dice."""
    toRoll = input('Roll all the dice? (y/n): ')
    toRoll = str(toRoll)
    if toRoll == 'y' or toRoll == 'Y':
        status = "200 Roll Dice"
    else:
        status = "500 Game Over"
    return status


def bidPrompt2(f, v):
    """Generates Question As to Whether Client Wants to Make a Bid or Call Out the Liar."""
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


def bidPrompt(f, v):
    """Generates Question As to Whether Client Wants to Make the Initial Bid."""
    toBid = input('Would You Like to Make a Bid? (y/n): ')
    toBid = str(toBid)
    if toBid == 'y' or toBid == 'Y':
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
    file = open("bid.tmp","w")
    file.write(frequency + " " + value)
    file.close()
    return "300 Bid " + frequency + " " + value
    

    

def challenge(roll, msg):
    msg = msg.split(' ');
    if (msg[3] == "Challenge"):
        print('Client roll is: ' + roll)
        print('Opponent\'s roll is: ' + msg[4])
        alldice = roll + msg[4]
        cfreq = msg[5]
        cvalue = msg[6]
        correctcount = alldice.count(cvalue)

        if (int(correctcount) != int(cfreq)):
            print ("LIAR!! There are Actually " + str(correctcount) + " " + str(cvalue) + "'s present!")
            return "306 WIN"
        else:
            print ("You Win!  There are Actually " + str(correctcount) + " " + str(cvalue) + "'s present!")
            return "306 LOSE"
    else:    
        print('Client roll is: ' + roll)
        print('Opponent\'s roll is: ' + msg[5])
        alldice = roll + msg[5]
        cfreq = msg[3]
        cvalue = msg[4]
        correctcount = alldice.count(cvalue)

        if (int(correctcount) != int(cfreq)):
            print ("You Win! There are Actually " + str(correctcount) + " " + str(cvalue) + "'s present!")
            return "306 LOSE"
        else:
            print ("NO LIES!!  There are Actually " + str(correctcount) + " " + str(cvalue) + "'s present!")
            return "306 WIN"
  




# s       = socket
# msg     = initial message being processed
def processMsgs(s, msg):
    if (msg.startswith('105')):
        m = RollDice()
        s.send(m.encode())
        if (m.startswith('500')):
            s.close()
            print("Game Over!")
            exit();
        return 1
    
    if (msg.startswith('205')):
        smsg = msg.split(' ');
        pdice = smsg[4][0:9]
        file = open("dice.tmp","w")
        file.write(smsg[4])
        file.close()
        print ("Server Sent the Following Dice: " + pdice)
        bid = bidPrompt(0,0)
        if (bid == -1):
            s.send("500 Game Over".encode())
            s.close() 
            print("Game Over!")
            exit();
        else:
            mbid = make_bid(bid, msg)
            if mbid == -1:
                s.send("500 Game Over".encode())
                s.close() 
                print("Game Over!")
                exit()
            else:
                s.send(mbid.encode())
                print ("Awaiting Response from Server.....")
        return 1
    
    if (msg.startswith('305')):
        #Bid ACK Messages Here...
        file = open("dice.tmp", "r") 
        pdice = file.read()
        file.close()
        smsg = msg.split(' ');
        if (smsg[3] == "Challenge"):
            print("Server Challenges Your Bid .... ")
            s.send(challenge(pdice[0:9],msg).encode());
            #send challenge result to server
            s.close() 
            print("Game Over!")
            exit()
        else:
            cfreq = smsg[3]
            cvalue = smsg[4]
            print("Server Returns With Bid \n" + " Die Face Value: " + cvalue + "\n Die Minimum Count: " + cfreq)
            bid = bidPrompt2(cfreq, cvalue)
            if (bid == -1):
                 print ("Calling Out the Liar....")
                 s.send(challenge(pdice[0:9],msg).encode());
                 #send challenge result to server
                 s.close() 
                 print("Game Over!")
                 exit()
                 
            else:
                s.send(make_bid(bid, msg).encode())
                print ("Awaiting Response from Server.....")
    return 1

    if (msg.startswith('306')):
        gamemsg = msg.split(' ')
        if gamemsg[1] == "WIN":
            print("Server Lost!")
        else:
            print("Server WON!")
        s.close()
        print("Game Over!")
        exit();
    
    if (msg.startswith('500')):
        s.close()
        print("Game Over!")
        exit();
    pass
                

def main():
    """Driver function for the project"""
    args = sys.argv
    if len(args) != 3:
        print ("Please supply a server address and port.")
        sys.exit()
    serverHost = str(args[1])       # The remote host
    serverPort = int(args[2])       # The same port as used by the server
    
    print("\nClient of Rhon-Kaniel BRamwell")
    print('''
      The dice in this program have a face value in the range 1--6.
    No error checking is done, so ensure that the bids are in the correct range.
    Follow the on-screen instructions.
    ''')

    s = socket(AF_INET,SOCK_STREAM)
    s.connect((serverHost,serverPort))
    s.send(serverHello().encode())
    # Handle the data that is read through the socket by using processMsgs(s, msg)
    status = 1
    while (status == 1):
        msg = s.recv(1024).decode('utf-8')
        print(msg);
        if not msg:
            status = -1
        else:
            status = processMsgs(s, msg)
    if status < 0:
        print("Invalid data received. Closing")
    s.close() 
    print("Closed connection socket")
if __name__ == "__main__":
    main()

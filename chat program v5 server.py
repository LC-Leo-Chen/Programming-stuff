import socket,threading,time as t

#init server
server=socket.socket()
ip_addr=socket.gethostbyname(socket.gethostname())
print(ip_addr)
server.bind((ip_addr,int(input('enter port: '))))
server.listen()

#init variables
Names=[]#List of registered Names
Name_pass={}#Returns password when given Name (all registered)
R_Names={}#Returns connection when given Name (online) for Receive mode
S_Names={}#Returns connection when given Name (online) for Send mode
msgs=[]#All public messages
R_msgs={}#returns messages corresponding when given Name (both public and private)
prs_queue={}#A queue to process the messages (so no overlap will happen, especially when dealing with long data)

#function for login and register
def account_prs(connection,T):
    global Names,Name_pass,R_Names,S_Names,msgs,R_msgs
    action=connection.recv(1024)
    connection.send(b'confirm')
    Name=''
    if action==b'register':
        #Get username that is to be registered
        Name=connection.recv(1024).decode()
        #Check username
        while Name in Names or Name=='/end':
            connection.send(b'False')
            Name=connection.recv(1024).decode()
        connection.send(b'ok')
        #Get password
        passw=connection.recv(1024).decode()
        connection.send(b'ok')
        #Update info
        Names.append(Name)
        Name_pass[Name]=passw
        #set up the messages corresponding to the Name
        R_msgs[Name]=[]        
        for i in msgs:
            R_msgs[Name].append(i)
        print('%s has successfully registered as %s'%(str(info),Name))
    elif action==b'login':
        #Get username that is to be logged in
        Name=connection.recv(1024).decode()
        #Check username Layer 1
        while (Name in Names)==False:
            connection.send(b'False')
            Name=connection.recv(1024).decode()
        tmp={}
        if T=='S':
            tmp=S_Names
        else:
            tmp=R_Names
        #Check username Layer 2 (to see if will overlap)
        while tmp.get(Name)!=None:
            connection.send(b'used')
            Name=connection.recv(1024).decode()
            while (Name in Names)==False:
                connection.send(b'False')
                Name=connection.recv(1024).decode()
        connection.send(b'ok')
        #Check password
        while connection.recv(1024).decode()!=Name_pass[Name]:
            connection.send(b'False')
        connection.send(b'ok')
        print('%s has successfully logged in as %s'%(str(info),Name))
    else:
        print('%s has attempted a nonexistent action %s'%(str(info),Name))
        print('No such action as %s'%action.decode())
        print(action)
        connection.close()
        return None
    if T=='S':
        S_Names[Name]=connection
    else:
        R_Names[Name]=connection
    return Name
#function for processing messages in the queue
def prs_todo(connection):
    try:
        #First in First Out
        while True:
            while len(prs_queue[connection])>0:
                if prs_queue[connection][0][1]==None:
                    connection.send(b'T')
                    connection.recv(1024)
                else:
                    connection.send(b'F')
                    connection.recv(1024)
                    for i in range(1,3):
                        connection.send(prs_queue[connection][0][i])
                        connection.recv(1024)
                connection.send(str(len(prs_queue[connection][0][0])).encode())
                connection.recv(1024)
                connection.sendall(prs_queue[connection][0][0])
                connection.recv(1024)
                del prs_queue[connection][0]
    except:
        #this is to get rid of the messy error message when people disconnect (normal)
        pass
#function for processing messages (put in queue or saving it to list corresponding to Name
def msg_prs(NAME,MSG):
    global R_msgs,R_Names
    #MSG is in byte form
    #Append to the independent list of msg of the name
    R_msgs[NAME].append(MSG)
    #Send to the user directly if he/she is online
    if R_Names.get(NAME)!=None:
        prs_queue[R_Names[NAME]].append(MSG)
#function for processing received message (bad name isn't it?)
def relay(connection,trgts,Name,text):
    T=connection.recv(1024)
    connection.send(b'confirm')
    fn=None
    ft=None
    #process file stuff if the message is a file
    if T==b'F':
        fn=connection.recv(1024)
        connection.send(b'confirm')
        ft=connection.recv(1024)
        connection.send(b'confirm')
    L=int(connection.recv(1024).decode())
    connection.send(b'confirm')
    #get the full message (to the full length)
    nmsg=b''
    while len(nmsg)!=L:
        nmsg+=connection.recv(1024)
    connection.send(b'confirm')
    nmsg=[nmsg,fn,ft]
    if T==b'T':
        if text=='public':
            nmsg[0]=(Name+(' [%s] : '%text)+nmsg[0].decode()+('\n%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S'))).encode()
        else:
            nmsg[0]=(Name+(' [%s]%s : '%(text,trgts))+nmsg[0].decode()+('\n%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S'))).encode()
    else:
        nmsg[1]=(nmsg[1].decode()+' '+Name+(' [%s] %s'%(text,t.strftime('%Y_%m_%d  %H-%M-%S')))).encode()
    for i in trgts:
        msg_prs(i,nmsg)
    return nmsg
#Overall processing for the connections
def process(connection,info):
    global Names,Name_pass,R_Names,S_Names,msgs,R_msgs
    try:
        user_type=connection.recv(1024)
        connection.send(b'confirm')
        Name=''
        if user_type==b'send':
            try:
                Name=account_prs(connection,'S')
                if Name==None:
                    return 'blocked'
                print('-'*10)
                print('Send mode: '+str(len(S_Names))+': '+str(list(S_Names.keys())))
                print('Receive mode: '+str(len(R_Names))+': '+str(list(R_Names.keys())))
                conmsg=[('System: %s\'s send mode program has connected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(conmsg)
                for i in range(len(R_msgs)):
                    msg_prs(list(R_msgs.keys())[i],conmsg)
                #Send mode process
                while True:
                    msgT=connection.recv(1024)
                    connection.send(b'confirm')
                    if msgT==b'/getnames':
                        #provide current active names
                        for i in Names:
                            connection.send(i.encode())
                            connection.recv(1024)
                        connection.send(b'/end')
                        connection.recv(1024)
                    elif msgT==b'/spec':
                        #send privately
                        #get targets
                        targets=[]
                        while True:
                            target=connection.recv(1024).decode()
                            while target not in R_msgs.keys() and target!='/end':
                                connection.send(b'False')
                                target=connection.recv(1024).decode()
                            connection.send(b'ok')
                            if target=='/end':
                                break
                            targets.append(target)
                        #add yourself to the recipients (so the user can check on to the message later)
                        targets.append(Name)
                        #relay the message
                        relay(connection,targets,Name,'private')
                    elif msgT==b'/public':
                        #send publicly
                        #relay the message
                        nmsg=relay(connection,list(R_msgs.keys()),Name,'public')
                        #Append the message to the public msg list
                        msgs.append(nmsg)
            #Error processing (like disconnecting) for send mode
            except Exception as e:
                print('-'*10)
                print(e)
                if Name in S_Names.keys():
                    del S_Names[Name]
                print('disconnection')
                #send disconnection message
                dismsg=[('System: %s\'s send mode program has disconnected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(dismsg)
                for i in range(len(R_msgs)):
                    msg_prs(list(R_msgs.keys())[i],dismsg)
                print('Send mode: '+str(len(S_Names))+': '+str(list(S_Names.keys())))
                print('Receive mode: '+str(len(R_Names))+': '+str(list(R_Names.keys())))
        elif user_type==b'recv':
            try:
                Name=account_prs(connection,'R')
                if Name==None:
                    return 'blocked'
                print('-'*10)
                print('Send mode: '+str(len(S_Names))+': '+str(list(S_Names.keys())))
                print('Receive mode: '+str(len(R_Names))+': '+str(list(R_Names.keys())))
                conmsg=[('System: %s\'s read mode program has connected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(conmsg)
                for i in range(len(R_msgs)):
                    if list(R_msgs.keys())[i]==Name:#exception since we don't want to send it directly for now
                        R_msgs[Name].append(conmsg)
                    else:
                        msg_prs(list(R_msgs.keys())[i],conmsg)
                #copy the messages from stored to active
                prs_queue[connection]=[]
                for i in R_msgs[Name]:
                    prs_queue[connection].append(i)
                todo=threading.Thread(target=prs_todo,args=(connection,))
                todo.start()
                while True:
                    #check if connection active since there may not be any new messages,
                    #the connection may have been down already which is left unnoticed
                    #An exception will be triggered by the send command if the connection is down
                    #I put an empty byte string so no actual message is sent,
                    #so it won't interfere if it is still active 
                    connection.send(b'')
            #Error processing (like disconnecting) for read mode
            except Exception as e:
                print('-'*10)
                print(e)
                if Name in R_Names.keys():
                    del R_Names[Name]
                if connection in prs_queue.keys():
                    del prs_queue[connection]
                print('disconnection')
                #send disconnection message
                dismsg=[('System: %s\'s read mode program has disconnected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(dismsg)
                for i in range(len(R_msgs)):
                    msg_prs(list(R_msgs.keys())[i],dismsg)
                print('Send mode: '+str(len(S_Names))+': '+str(list(S_Names.keys())))
                print('Receive mode: '+str(len(R_Names))+': '+str(list(R_Names.keys())))
        else:
            print('CONNECTION TYPE UNSPECIFIED!!!')
            connection.close()
    except:
        pass
#Main
while True:
    #server.accept() will return two values when users connect
    user,info=server.accept()
    #process the connections simultaneously while continuing to accept new conenctions
    function=threading.Thread(target=process,args=(user,info))
    function.start()

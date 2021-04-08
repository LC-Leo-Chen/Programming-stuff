import socket,threading,time as t

server=socket.socket()
ip_addr=socket.gethostbyname(socket.gethostname())
print(ip_addr)
server.bind((ip_addr,int(input('enter port: '))))
server.listen()

S_users=[]
R_users=[]
Names=[]
Name_pass={}
R_Names={}
S_Names={}
msgs=[]
R_msgs={}
prs_queue={}

def account_prs(connection,T):
    global S_users,R_users,Names,Name_pass,R_Names,S_Names,msgs,R_msgs
    action=connection.recv(1024)
    connection.send(b'confirm')
    Name=''
    if action==b'register':
        Name=connection.recv(1024).decode()
        while Name in Names or Name=='/end':
            connection.send(b'False')
            Name=connection.recv(1024).decode()
        connection.send(b'ok')
        passw=connection.recv(1024).decode()
        connection.send(b'ok')
        Names.append(Name)
        Name_pass[Name]=passw
        R_msgs[Name]=[]
        for i in msgs:
            R_msgs[Name].append(i)
        print('%s has successfully registered as %s'%(str(info),Name))
    elif action==b'login':
        Name=connection.recv(1024).decode()
        while (Name in Names)==False:
            connection.send(b'False')
            Name=connection.recv(1024).decode()
        if T=='S':
            while S_Names.get(Name)!=None:
                connection.send(b'used')
                Name=connection.recv(1024).decode()
                while (Name in Names)==False:
                    connection.send(b'False')
                    Name=connection.recv(1024).decode()
            connection.send(b'ok')
        else:
            while R_Names.get(Name)!=None:
                print(R_Names.get(Name))
                connection.send(b'used')
                Name=connection.recv(1024).decode()
                while (Name in Names)==False:
                    connection.send(b'False')
                    Name=connection.recv(1024).decode()
            connection.send(b'ok')            
        while connection.recv(1024).decode()!=Name_pass[Name]:
            connection.send(b'False')
        connection.send(b'ok')
        print('%s has successfully logged in as %s'%(str(info),Name))
    else:
        print('Failed setup attempt: no such action as %s'%action.decode())
        print(action)
        connection.close()
    return Name
def prs_todo(connection):
    try:
        while True:
            while len(prs_queue[connection])>0:
                if prs_queue[connection][0][1]==None:
                    connection.send(b'T')
                    connection.recv(1024)
                else:
                    connection.send(b'F')
                    connection.recv(1024)
                    connection.send(prs_queue[connection][0][1])
                    connection.recv(1024)
                    connection.send(prs_queue[connection][0][2])
                    connection.recv(1024)
                connection.send(str(len(prs_queue[connection][0][0])).encode())
                connection.recv(1024)
                connection.sendall(prs_queue[connection][0][0])
                connection.recv(1024)
                del prs_queue[connection][0]
    except:
        #this is to get rid of the messy error message when people disconnect (normal)
        pass
def msg_prs(NAME,MSG):
    global R_msgs,R_Names
    #MSG is in byte form
    #Append to the independent list of msg of the name
    print('start msg processing')
    R_msgs[NAME].append(MSG)
    print('message saved to %s \'s account msg list'%NAME)
    #Send to the user directly if he/she is online
    if R_Names.get(NAME)!=None:
        prs_queue[R_Names[NAME]].append(MSG)
        print('message sent directly to %s'%NAME)
    print('complete')
def send_prs(connection):
    T=connection.recv(1024)
    connection.send(b'confirm')
    fn=None
    ft=None
    if T==b'F':
        fn=connection.recv(1024)
        connection.send(b'confirm')
        ft=connection.recv(1024)
        connection.send(b'confirm')
    L=int(connection.recv(1024).decode())
    connection.send(b'confirm')
    msg=b''
    while len(msg)!=L:
        msg+=connection.recv(1024)
    connection.send(b'confirm')
    msg=[msg,fn,ft]
    return T,msg
def process(connection,info):
    global S_users,R_users,Names,Name_pass,R_Names,S_Names,msgs,R_msgs
    try:
        user_type=connection.recv(1024)
        connection.send(b'confirm')
        Name=''
        if user_type==b'send':
            S_users.append(connection)
            print('-'*10)
            print('S_users: '+str(len(S_users)))
            print('R_users: '+str(len(R_users)))
            try:
                Name=account_prs(connection,'S')
                S_Names[Name]=connection
                print('S_Names: '+str(list(S_Names.keys())))
                print('R_Names: '+str(list(R_Names.keys())))
                conmsg=[('System: %s\'s send mode program has connected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(conmsg)
                for i in range(len(R_msgs)):
                    msg_prs(list(R_msgs.keys())[i],conmsg)
                #Send mode process
                while True:
                    msgT=connection.recv(1024)
                    connection.send(b'confirm')
                    if msgT==b'/getnames':
                        for i in Names:
                            connection.send(i.encode())
                            connection.recv(1024)
                        connection.send(b'/end')
                        connection.recv(1024)
                    elif msgT==b'/spec':
                        #send privately
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
                        targets.append(Name)
                        T,pmsg=send_prs(connection)
                        if T==b'T':
                            pmsg[0]=(Name+(' [private]%s : '%(targets))+pmsg[0].decode()+('\n%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S'))).encode()
                        else:
                            pmsg[1]=(pmsg[1].decode()+' '+Name+(' [private] %s'%t.strftime('%Y_%m_%d  %H-%M-%S'))).encode()
                        for i in targets:
                            msg_prs(i,pmsg)
                    elif msgT==b'/public':
                        #send publicly
                        T,nmsg=send_prs(connection)
                        if T==b'T':
                            nmsg[0]=(Name+' [public] : '+nmsg[0].decode()+('\n%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S'))).encode()
                        else:
                            nmsg[1]=(nmsg[1].decode()+' '+Name+(' [public] %s'%t.strftime('%Y_%m_%d  %H-%M-%S'))).encode()
                        #Append to the public msg list
                        msgs.append(nmsg)
                        for i in range(len(R_msgs)):
                            msg_prs(list(R_msgs.keys())[i],nmsg)
            #Error processing (like disconnecting)
            except Exception as e:
                print('-'*10)
                print(e)
                S_users.remove(connection)
                if Name in S_Names.keys():
                    del S_Names[Name]
                print('disconnection')
                dismsg=[('System: %s\'s send mode program has disconnected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(dismsg)
                for i in range(len(R_msgs)):
                    msg_prs(list(R_msgs.keys())[i],dismsg)
                print('S_Names: '+str(list(S_Names.keys())))
                print('R_Names: '+str(list(R_Names.keys())))
                print('S_users: '+str(len(S_users)))
                print('R_users: '+str(len(R_users)))
        elif user_type==b'recv':
            R_users.append(connection)
            print('-'*10)
            print('S_users: '+str(len(S_users)))
            print('R_users: '+str(len(R_users)))
            try:
                Name=account_prs(connection,'R')
                print('S_Names: '+str(list(S_Names.keys())))
                print('R_Names: '+str(list(R_Names.keys())))
                conmsg=[('System: %s\'s read mode program has connected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(conmsg)
                for i in range(len(R_msgs)):
                    if list(R_msgs.keys())[i]==Name:
                        R_msgs[Name].append(conmsg)
                    else:
                        msg_prs(list(R_msgs.keys())[i],conmsg)
                #Receive mode process
                #Send in the current messages in the list
                prs_queue[connection]=[]
                for i in R_msgs[Name]:
                    prs_queue[connection].append(i)
                #To enable direct sending (via queue) only after init
                #to prevent overlapping and sending two same msgs (very unlikely though)
                R_Names[Name]=connection
                todo=threading.Thread(target=prs_todo,args=(connection,))
                todo.start()
                while True:
                    #check if connection active since there may not be any new messages,
                    #the connection may have been down already which is left unnoticed
                    #An exception will be triggered by the send command if the connection is down
                    #I put an empty byte string so no actual message is sent,
                    #so it won't interfere if it is still active 
                    connection.send(b'')
            #Error processing (like disconnecting)
            except Exception as e:
                print('-'*10)
                print(e)
                R_users.remove(connection)
                if Name in R_Names.keys():
                    del R_Names[Name]
                if connection in prs_queue.keys():
                    del prs_queue[connection]
                print('disconnection')
                dismsg=[('System: %s\'s read mode program has disconnected\n%s'%(Name,('%s\n\n'%t.strftime('%Y/%m/%d %A, %B, %H:%M:%S')))).encode(),None,None]
                msgs.append(dismsg)
                for i in range(len(R_msgs)):
                    msg_prs(list(R_msgs.keys())[i],dismsg)
                print('S_Names: '+str(list(S_Names.keys())))
                print('R_Names: '+str(list(R_Names.keys())))
                print('S_users: '+str(len(S_users)))
                print('R_users: '+str(len(R_users)))
        else:
            print('CONNECTION USER TYPE UNSPECIFIED!!!')
            connection.close()
    except Exception as e:
        print('ERROR')
        print(e)
while True:
    #server.accept() will return two values when users connect

    #First is the information that allows us to send and receive data from the user.
    #We call it "user" here.
    
    #Second is the ip address and port number of the user.
    #We call it "info" here.
    user,info=server.accept()
    function=threading.Thread(target=process,args=(user,info))
    function.start()

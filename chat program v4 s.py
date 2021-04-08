import socket
print('CHAT PROGRAM SEND MODE')
connection=socket.socket()
connection.connect((input('enter the ip address of the server you wish to connect to: ')
,int(input('enter the port of the server you wish to connect to: '))))
connection.send(b'send')
connection.recv(1024)
def login():
    connection.send(b'login')
    connection.recv(1024)
    Name=input('Enter name to log in: ')
    while not Name or len(Name)>1024:
        Name=input('Enter name to log in: ')
    connection.send(Name.encode())
    rdata=connection.recv(1024)
    while rdata==b'False' or rdata==b'used':
        if rdata==b'False':
            print('This name doesn\'t exist as an available account in use')
        else:
            print('Somebody else is logged in with this name already')
        Name=input('Enter Name to log in: ')
        while not Name or len(Name)>1024:
            Name=input('Enter name to log in: ')
        connection.send(Name.encode())
        rdata=connection.recv(1024)
    passw=input('Enter password for this name: ')
    while not passw or len(passw)>1024:
        passw=input('Enter password for ths name: ')
    connection.send(passw.encode())
    while connection.recv(1024)==b'False':
        print('Password incorrect')
        passw=input('Enter password for this name: ')
        while not passw or len(passw)>1024:
            passw=input('Enter password for ths name: ')
        connection.send(passw.encode())
def register():
    connection.send(b'register')
    connection.recv(1024)
    Name=input('Enter name to register: ')
    while not Name or len(Name)>1024:
        Name=input('Enter name to register: ')
    connection.send(Name.encode())
    while connection.recv(1024)==b'False':
        print('Somebody registered this name already')
        Name=input('Enter name to register: ')
        while not Name or len(Name)>1024:
            Name=input('Enter name to register: ')
        connection.send(Name.encode())
    passw=input('Enter password for this name: ')
    while not passw or len(passw)>1024:
        passw=input('Enter password for this name: ')
    connection.send(passw.encode())
    connection.recv(1024)
print('A registered name can provide service for a pair of send and receive mode only')
action=input('Register (will log you in afterwards)(R) or Login (L)')
stat=input('Are you sure ("Y" to confirm)')
while (action!='R' and action!='L') or stat!='Y':
    action=input('Register (will log you in afterwards)(R) or Login (L)')
    stat=input('Are you sure ("Y" to confirm)')
if action=='L':
    login()
else:
    register()
print('Account setup complete')
def prs_msg(atext):
    T=input('enter msg type (file=F,text=T): ')
    while T!='F' and T!='T':
        print('Enter F or T (file or text)')
        T=input('enter msg type (file=F,text=T): ')
    msg=b'BLANK'
    if T=='T':
        #tell the server it is a text message
        connection.send(T.encode())
        connection.recv(1024)
        print(atext,end='')
        msg=input('')
        while not msg:
            print('msg cannot be empty')
            print(atext,end='')
            msg=input('')
        msg=msg.encode()
    else:
        fn=''
        ft=''
        while msg==b'BLANK':
            try:
                route=input('enter file route (use "/" instead of "\\")')
                start=0
                for i in range(len(route)):
                    if route[len(route)-1-i]=='/':
                        start=len(route)-i
                        break
                fn=''
                ft=''
                for i in range(start,len(route)):
                    if route[i]=='.':
                        for j in range(i,len(route)):
                            ft+=route[j]
                        break
                    fn+=route[i]
                file=open(route,'rb')
                msg=file.read()
            except:
                print('error')
        print('sending file...')
        #tell the server it is a file message
        connection.send(T.encode())
        connection.recv(1024)
        #tell the server what type of file it is
        connection.send(fn.encode())
        connection.recv(1024)
        #tell the server what the name of the file is
        connection.send(ft.encode())
        connection.recv(1024)
    #tell the server how much data is expected
    connection.send(str(len(msg)).encode())
    connection.recv(1024)
    #send data
    connection.sendall(msg)
    connection.recv(1024)
while True:
    print('\nTo request for current names (accounts), enter "/getnames"')
    print('To send to specific people, enter "/spec"')
    print('To send to all people, enter "/public"')
    mode=input('enter mode: ')
    while mode!='/getnames' and mode!='/spec' and mode!='/public':
        print('\nchoose a type')
        print('To request for current names (accounts), enter "/getnames"')
        print('To send to specific people, enter "/spec"')
        print('To send to all people, enter "/public"')
        mode=input('enter mode: ')
    connection.send(mode.encode())
    connection.recv(1024)
    if mode=='/getnames':
        #It is not possible to not logging in a name but able to use my program to
        #receive and send messages
        #lazy way for formatting below
        print('Names:')
        name='-'*20
        #print the name and receive the next afterwards,
        #this avoids printing the /end
        while name!='/end':
            print(name)
            name=connection.recv(1024).decode()
            connection.send(b'confirm')
        print('-'*20)
    elif mode=='/spec':
        print('The program will include the sender as a recipient so the sender can see what he/she sent later on\n')
        while True:
            target=input('Enter account (name) to send to (enter nothing to finish): ')
            if target=='':
                target='/end'
            connection.send(target.encode())
            while connection.recv(1024)==b'False':
                print('Name not found')
                target=input('Enter account (name) to send to (enter nothing to finish): ')
                if target=='':
                    target='/end'
                connection.send(target.encode())
            if target=='/end':
                break
        prs_msg('enter msg for private send: ')
    else:
        prs_msg('enter msg for public send: ')

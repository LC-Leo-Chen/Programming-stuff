import socket
print('CHAT PROGRAM RECEIVE MODE')
connection=socket.socket()
connection.connect((input('enter the ip address of the server you wish to connect to: ')
,int(input('enter the port of the server you wish to connect to: '))))
connection.send(b'recv')
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
print('Account setup complete\n')
while True:
    msg_T=connection.recv(1024)
    connection.send(b'confirm')
    fn=None
    ft=None
    if msg_T==b'F':
        fn=connection.recv(1024).decode()
        connection.send(b'confirm')
        ft=connection.recv(1024).decode()
        connection.send(b'confirm')
    msg_L=int(connection.recv(1024).decode())
    connection.send(b'confirm')
    msg=b''
    while len(msg)!=msg_L:
        msg+=connection.recv(1024)
    connection.send(b'confirm')
    if msg_T==b'T':
        print(msg.decode(),end='')
    else:
        file=open(fn+ft,'wb+')
        file.write(msg)
        file.close()
        print('Received a file message: %s\n'%(fn+ft))

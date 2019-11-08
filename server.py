#python socket server by Leo Chen
import socket,_thread,time as t
n=socket.gethostname()
host=socket.gethostbyname(n)
print('server: '+host)
port=int(input('enter port: '))
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen(5)
users_online=0
print('you might want to check your firewall settings and other\npossible problems and fix them')
print('server starts')
file=open('msgs.txt','a+')
file=open('msgs.txt','r')
msg=file.readlines()
users=[]
def stuff(users,client):
    try:
        if client in users:
            users.remove(client)
    except:
        stuff(users,client)
def handle(client,addr):
    try:
        print('\nip: <'+addr[0]+'> has connected\n')
        print('users: ',len(users))
        for i in msg:
            client.send((i+'\n').encode())
        while True:
            cmsg=client.recv(1024).decode()
            if cmsg!='':
                time=t.strftime('%Y/%m/%d %H:%M:%S',t.localtime())
                msg.append('<'+addr[0]+'>'+': '+cmsg+'\n\n'+time+'\n\n')
                file=open('msgs.txt','a+')
                file.write('<'+addr[0]+'>'+': '+cmsg+'\n\n'+time+'\n\n')
                file.close()
                for j in users:
                    j.send(('<'+addr[0]+'>'+': '+cmsg+'\n\n'+time+'\n\n').encode())
    except Exception as e:
        print(e)
        print('\nip: <'+addr[0]+'> has disconnected\n')
        stuff(users,client)
        print('users: ',len(users))
def start_server():
    while True:
        client,addr=server.accept()
        users.append(client)
        _thread.start_new_thread(handle,(client,addr,))
start_server()

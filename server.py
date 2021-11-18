import socket
import threading
from queue import Queue
import datetime

def Send(group, send_queue): 
    print('Send Start') 
    while True: 
        try:
            recv = send_queue.get() 
            if recv == 'new': # 새 클라이언트의 연결을 알림
                break   # 새 클라이언트가 들어올 때마다 스레드가 종료되므로, Send 스레드는 하나만 존재하게 됨
            
            for conn in group: 
                msg = '['+datetime.datetime.now().strftime('%H:%M:%S')+'] '+str(recv[0])
                if recv[1] != conn:
                    try:conn.send(bytes(msg.encode()))
                    except:pass
                else: 
                    pass
        except: 
            pass

def Recv(conn, count, send_queue): 
    print(str(count) + ' Start')
    try:
        while True: # Recv 스레드는 여러 개 존재 가능함
            data = conn.recv(1024).decode()
            send_queue.put([data, conn, count])
    except:
        pass


if __name__ == '__main__': 
    send_queue = Queue() 
    HOST = ''
    PORT = 9000
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
    server_sock.bind((HOST, PORT))
    server_sock.listen(8) # 접속수
    count = 0 
    group = []
    while True: 
        count = count + 1 
        conn, addr = server_sock.accept()
        group.append(conn)
        print('Connected ' + str(addr)) 
        
        # Send 스레드에 새로운 클라이언트가 들어왔다고 알림
        if count > 1: 
            send_queue.put('new') 
            
        send_thread = threading.Thread(target=Send, args=(group, send_queue,)) 
        recv_thread = threading.Thread(target=Recv, args=(conn, count, send_queue,))
        send_thread.start() 
        recv_thread.start()
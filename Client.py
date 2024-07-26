import socket
import random
import sys


HOST = '127.0.0.1'
PORT = int(sys.argv[1])

input1 = sys.argv[2]
input2 = sys.argv[3]
wait_time = int(sys.argv[4])
question = input1 +'\n'+input2

ID = str(random.randint(0,65535))+'\n'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = f"{ID}{question}"

target_addr = (HOST, PORT)
sock.sendto(message.encode('utf-8'), target_addr)

sock.settimeout(wait_time)

try:
    data, addr = sock.recvfrom(1024)
    data = data.decode('utf-8')

    ID_rcv = ''
    for i in range(len(data)):
        if data[i] == '\n':
            break
        else:
            ID_rcv += data[i]

    answer = data

    ID_rcv = ID_rcv.split()[1]

    if int(ID_rcv) != int(ID):
        print('wrong ID')
    else:
        print(answer)

except TimeoutError:
    print('Timed out')
    pass


sock.close()

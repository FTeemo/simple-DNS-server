import socket
import time
import threading
import random
import logging
import sys

def handle(serve_sock,client_addr,data):

    delay = random.randint(0,4)
    time.sleep(delay)
    data = data_decode(data)

    logging.warning('rcv %s: %s %s %s (delay:%ds)',client_addr[1],data[0],data[1],data[2],delay)

    ID = data[0] + '\n'
    answer = get_answer(data)
    answer = 'ID: ' + str(ID) + '\n' + 'QUESTION SECTION:\n' + data[1] + '  ' + data[2] + '\n\n' + answer
            # answer = ID + answer
    answer = answer.encode('utf-8')
    serve_sock.sendto(answer, client_addr)
    logging.warning('snd %s: %s %s %s', client_addr[1], data[0], data[1], data[2])

def data_decode(data_receive):
    data = data_receive.decode('utf-8')
    data_split = []
    for i in data.splitlines():
        data_split.append(i)
    return data_split

def get_authority(domain_name,result):
    global DNS_record
    possible_result = []
    result_list = []
    if result == 'ANSWER SECTION:\n':
        result = 'AUTHORITY SECTION:\n'
    else:
        result += 'AUTHORITY SECTION:\n'

    for i in range(len(DNS_record)):
        if DNS_record[i].split()[0] in domain_name:
            possible_result.append(DNS_record[i])

    max_len = 0
    for i in range(len(possible_result)):
        if max_len < len(possible_result[i].split()[0]):
            max_len = len(possible_result[i].split()[0])

    for i in range(len(possible_result)):
        if len(possible_result[i].split()[0]) == max_len:
            result += possible_result[i] + '\n'
            result_list.append(possible_result[i])
    result += '\nADDITIONAL SECTION:\n'
    for i in range(len(result_list)):
        name_now = result_list[i].split()[2]
        for j in range(len(DNS_record)):
            judge1 = DNS_record[j].split()[0]
            judge2 = DNS_record[j].split()[1]
            if name_now == judge1 and judge2 == 'A':
                result += DNS_record[j] + '\n'
    return result




def get_answer(data):
    record_useful = []
    answer = 'ANSWER SECTION:\n'
    global DNS_record
    domain_name = data[1]
    type = data[2]
    for i in range(len(DNS_record)):
        if domain_name == DNS_record[i].split()[0]:
            record_useful.append(DNS_record[i])
    if type == 'CNAME':
        for i in range(len(record_useful)):
            if type == record_useful[i].split()[1]:
                answer += record_useful[i]
                break
        if answer == 'ANSWER SECTION:\n':
            answer = get_authority(domain_name,answer)

    elif type == 'A':
        for i in range(len(record_useful)):
            if type == record_useful[i].split()[1]:
                answer += record_useful[i] + '\n'
                break
        # if answer == 'ANSWER SECTION:\n':
        #     for i in range(len(record_useful)):
        #         if 'CNAME' == record_useful[i].split()[1]:
        #             newname = record_useful[i].split()[2].strip()
        #     for i in range(len(DNS_record)):
        #         if newname == DNS_record[i].split()[0] and type == DNS_record[i].split()[1]:
        #             answer += DNS_record[i] + '\n'
        #             break
        if answer == 'ANSWER SECTION:\n':
            newname = domain_name
            for i in range(len(DNS_record)):
                if newname == DNS_record[i].split()[0] and 'CNAME' == DNS_record[i].split()[1]:
                    newname = DNS_record[i].split()[2]
                    answer += DNS_record[i] + '\n'
                    for j in range(len(DNS_record)):
                        judge1 = DNS_record[j].split()[0]
                        judge2 = DNS_record[j].split()[1]
                        if newname == judge1 and type == judge2:
                            answer += DNS_record[j] + '\n'
        flag = 0
        judge_ans = answer[16:]
        len_judge = len(judge_ans.split())
        for i in range(1,int(len_judge/3)+1):
            if judge_ans.split()[3*i-2] == type:
                flag += 1

        if answer == 'ANSWER SECTION:\n':
            answer = get_authority(domain_name,answer)
        elif flag == 0:
            answer += '\n'
            answer = get_authority(newname,answer)

    elif type == 'NS':
        for i in range(len(record_useful)):
            if type == record_useful[i].split()[1]:
                answer += record_useful[i] + '\n'

    return answer


def main(PORT):
    global DNS_record
    with open('master.txt','r') as file:
        record = file.read()
        for i in record.splitlines():
            DNS_record.append(i)

    server_addr = (HOST,PORT)
    socketserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketserver.bind(server_addr)

    while True:
        data, addr = socketserver.recvfrom(1024)
        p = threading.Thread(target=handle, args=(socketserver,addr,data))
        p.start()




if __name__ == "__main__":
    HOST = '127.0.0.1'
    logging.basicConfig(format='%(asctime)s %(message)s')
    DNS_record = []
    try:
        PORT = int(sys.argv[1])
        main(PORT)
        print(f"DNS Server started on {HOST}")
    except IndexError:
        print("Please define a port number")
        pass





import os
import threading
from socket import *

import secert_data

address = secert_data.address
port = secert_data.port
buffersize = 1024
socket = socket(AF_INET, SOCK_STREAM)
socket.bind((address, port))
socket.listen(5)
ROOT_path = "/data1/{}/kaldi/egs/aishell/s5/data/test_game_data".format(secert_data.name)
decode_path = "/data1/{}/kaldi/egs/aishell/s5/exp/chain/tdnn_1a_sp/decode_test_own/log/".format(secert_data.name)
words = b'testing, 162342 revieve?'


def tcplink(sock, addr):
    head = clientsocket.recv(buffersize)
    head = head.decode()

    sr = head.split(" ")
    print("sr", sr)
    operation = sr[0]
    try:
        if operation == "register":
            clientsocket.send(words)
            user_name = sr[1]
            file_name = sr[2]
            file_size = sr[3]
            wav_path = ROOT_path + user_name + '/wavs/BAC009S0724W012/'
            trans_path = ROOT_path + user_name + '/transcript/aishell_transcript_v0.8.txt'
            os.system("mkdir -p {}".format(wav_path))
            os.system("mkdir -p {}".format(trans_path))
            os.system("touch {}".format(wav_path + file_name + ".wav"))
            os.system('echo "BAC009S0724W0121 **" > ' + trans_path)
            with open(wav_path + file_name + ".wav", "wb") as file:
                size = 0
                while True:
                    file_data = clientsocket.recv(buffersize)
                    if size > int(file_size):
                        break
                    if file_data:
                        size += 1024
                        file.write(file_data)
                    else:
                        break
        else:
            file_name = sr[1]
            file_size = sr[2]
            os.system("rm -fr " + ROOT_path)
            wav_path = ROOT_path + '/wavs/BAC009S0724W012/'
            trans_path = ROOT_path + '/transcript/'
            os.system("mkdir -p {}".format(ROOT_path))
            os.system("mkdir -p {}".format(wav_path))
            os.system("mkdir -p {}".format(trans_path))
            os.system("touch {}".format(wav_path + 'BAC009S0724W0121' + ".wav"))
            os.system('echo "BAC009S0724W0121 **" > ' + trans_path + 'aishell_transcript_v0.8.txt')
            with open(wav_path + 'BAC009S0724W0121' + ".wav", "wb") as file:
                size = 0
                while True:
                    file_data = clientsocket.recv(buffersize)
                    if size > int(file_size):
                        break
                    if file_data:
                        size += 1024
                        file.write(file_data)
                    else:
                        break

    except Exception as e:
        print("download erro ", e)
    else:
        print("success")

    if operation != "register":
        os.system("cd /data1/{}/kaldi/egs/aishell/s5;./run_decode_test_for_game.sh".format(secert_data.name))
        p = os.popen('sed -n "/^BAC009S0724W0121\|^$/ p" ' + decode_path + 'decode.1.log')
        result = p.readlines()
        p.close()
        # result=os.popen("bash run_test.sh "+file_name+".wav").readlines()
        print("result", result)
        clientsocket.send(result[-1].encode())
        print("send")
    # clientsocket.send(words)
    print("send finish")


# mess=clientsocket.recv(1024)
# print(mess.decode())
while True:
    print("waiting reciving with ip: {}  and port: {}".format(address, port))
    clientsocket, clientaddress = socket.accept()
    print("connected from ", clientaddress)
    # tcplink(clientsocket,clientaddress)
    t = threading.Thread(target=tcplink, args=(clientsocket, clientaddress))
    t.start()

socket.close()

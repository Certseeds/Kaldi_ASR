#!/usr/bin/env python
# coding=utf-8
'''
@Github: https://github.com/Certseeds
@Organization: SUSTech
@Author: Junyi
@Date: 2020-03-19 11:01:43
@LastEditors: nanoseeds
@LastEditTime: 2020-03-21 17:53:58
'''
import os
import threading
from socket import *

import secert_data

words: bytes = b''
words = b'testing, 162342 revieve?'
address = secert_data.address
port = secert_data.port
buffersize: int = 1024
ROOT_PATH: str = "/data1/{}/kaldi/egs/aishell/s5/".format(secert_data.name)
data_path: str = "{}{}".format(ROOT_PATH, "data/test_game_data/")  # origin ROOT_path
decode_path: str = "{}{}".format(ROOT_PATH, "exp/chain/tdnn_1a_sp/decode_test_own/log/")
decode_name: str = "run_decode_test_for_game.sh"
point_wav_file: str = "BAC009S0724W0121.wav"
command_str: str = "{}{}{}".format('sed -n "/^BAC009S0724W0121\|^$/ p" ', decode_path, 'decode.1.log')
print(command_str)
socket = socket(AF_INET, SOCK_STREAM)
socket.bind((address, port))
socket.listen(5)


def mkdir_p(file_name: str):
    if not os.path.exists(file_name):
        os.makedirs(file_name)


def recive_and_write_File(file_name: str, file_size: str, sock: socket):
    with open(file_name, "wb") as file:
        size: int = 0
        while True:
            file_data = sock.recv(buffersize)
            if size > int(file_size):
                break
            if file_data:
                size += len(file_data)
                file.write(file_data)
                if 1024 > len(file_data):
                    break
            else:
                break
    print("{} recive {} bytes is over".format(file_name, file_size))


def main():
    while True:
        print("waiting reciving with ip: {}  and port: {}".format(address, port))
        clientsocket, clientaddress = socket.accept()
        print("connected from ", clientaddress)
        t = threading.Thread(target=tcplink, args=(clientsocket, clientaddress))
        t.start()
    socket.close()


def tcplink(sock, addr):
    head = sock.recv(buffersize)
    head = head.decode()
    sr = head.split(" ")
    print("sr", sr)
    operation = sr[0]
    file_name = sr[1]
    file_size = sr[2]
    # sock.send(words)
    try:
        if operation == "register":
            user_name = sr[3]
            user_path: str = "{}{}".format(data_path, user_name)
            wav_path: str = "{}{}".format(user_path, "/wavs/BAC009S0724W012/")
            trans_path: str = "{}{}".format(user_path, "/transcript/aishell_transcript_v0.8.txt")
            recive_and_write_File("{}{}.wav".format(wav_path, file_name), file_size, sock)
        else:
            wav_path = "{}{}".format(data_path, "wavs/BAC009S0724W012/")
            trans_path = "{}{}".format(data_path, "transcript/")
            mkdir_p(data_path)
            mkdir_p(wav_path)
            mkdir_p(trans_path)
            with open("{}{}".format(trans_path, 'aishell_transcript_v0.8.txt'), "w") as file_5:
                file_5.write("BAC009S0724W0121 **")
                file_5.close()
            recive_and_write_File("{}{}".format(wav_path, point_wav_file), file_size, sock)
    except Exception as e:
        print("download error ", e)
    else:
        print("success")
    if operation != "register":
        os.system("cd {};./{}".format(ROOT_PATH, decode_name))
        with os.popen(command=command_str, mode="r") as p:
            result = p.readliens()
        print("result", result)
        sock.send(result[-1].encode())
    print("send finish")


if __name__ == '__main__':
    main()

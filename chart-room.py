import json
import threading
import socket
import traceback
import uuid
import time
import json_rpc

__author__ = 'pl'

id_addr_dict = {}
addr_id_dict = {}


def create_socket():
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print('create socket error.')
        return None


def login_thread(s, server_addr=('127.0.0.1', 5000), your_id=None):
    server_host, server_port = server_addr
    your_id = your_id or str(uuid.uuid1())[9:]
    while True:
        try:
            s.sendto(('{"jsonrpc":"2.0", "method":"login", "params":{"id": "' + your_id + '" }, "id":0}').encode('utf8'),
                     (server_host, server_port))
            time.sleep(60)
        except socket.error as e:
            traceback.print_exc()


def result_handler(result_obj):
    assert (result_obj['id'] == 0)
    for uid, addr in result_obj['result'].items():
        id_addr_dict[uid] = addr
        addr_id_dict[tuple(addr)] = uid


def print_msg(args, addr):
    print(addr_id_dict.get(tuple(addr), addr), ':', args['text'])


def recv_thread(s):
    while True:
        data, addr = s.recvfrom(1024)
        json_rpc.call_json_rpc(data, {'msg': print_msg}, result_handler, addr)


def send_thread(s):
    while True:
        text = input('>>')
        data = json.dumps(json_rpc.make_json_rpc_request('msg', {'text': text}))
        for addr in addr_id_dict.keys():
            s.sendto(data.encode('utf8'), addr)


def main():
    s = create_socket()
    login_t = threading.Thread(target=login_thread, args=(s, ('127.0.0.1', 5000)))
    recv_t = threading.Thread(target=recv_thread, args=(s,))
    send_t = threading.Thread(target=send_thread, args=(s,))

    login_t.start()
    recv_t.start()
    send_t.start()

    login_t.join()
    recv_t.join()
    send_t.join()


if __name__ == '__main__':
    main()

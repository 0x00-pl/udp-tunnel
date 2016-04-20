import json
import socket
import json_rpc

__author__ = 'pl'


global_user_dict = {}


def udp_login(args, addr):
    user_id = args['id']
    global_user_dict[user_id] = addr
    return global_user_dict


def recv_udp_login(port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", port))
    print("waiting on port:", port)
    while True:
        data, addr = s.recvfrom(1024)
        print(data, addr)
        result = json_rpc.call_json_rpc(data, {'login': udp_login}, None, addr)
        result = json.dumps(result).encode('utf8')
        print(result)
        s.sendto(result, addr)


def main():
    recv_udp_login()

if __name__ == '__main__':
    main()

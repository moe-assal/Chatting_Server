"""
network_client v1.0
done by:
Moe Assal
Contact:
mohammad.elassal04@gmail.com
phone number: +96171804948
location: Lebanon, Bekaa, Khirbet Rouha

v2.0:
    reboot without exiting
"""
import socket
import threading
HOST = "127.0.0.1"
PORT = 5431
my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def byte_to_string(bytes_):
    bytes_ = str(bytes_)
    return bytes_[2:len(bytes_) - 1]    # converts from "b'string_passed'" to "string_passed"


def receive_and_print_data():
    global received_data
    while True:
        try:
            received_data = my_sock.recv(1024)
            print(byte_to_string(received_data))
            received_data = None
        except ConnectionResetError:
            print("you have been disconnected by an error in the server, we will fix the problem as soon as possible.")
            print("please reboot")
            return False


def send_data():
    global input_data
    while True:
        try:
            input_data = input()
            my_sock.send(str.encode(input_data))
        except ConnectionResetError:
            return False


def initialize_client():
    try:
        my_sock.connect((HOST, PORT))
        received_data_thread = threading.Thread(target=receive_and_print_data, args=())
        send_data_thread = threading.Thread(target=send_data, args=())
        send_data_thread.setDaemon(True)
        received_data_thread.start()
        send_data_thread.start()
        return True
    except ConnectionRefusedError:
        print("server refused connection, we will fix the problem as soon as possible.")
        print("please reboot")
        return False


if __name__ == '__main__':
    initialize_client()

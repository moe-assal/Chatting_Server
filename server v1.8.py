"""
network_server v1.0
done by:
Moe Assal
Contact:
mohammad.elassal04@gmail.com
phone number: +96171804948
location: Lebanon, Bekaa, Khirbet Rouha

v2.0:
    -add the connection request deleter
v3.0:
    -add reset account and account delete options
    -add minimal requirements for a user name and a password
    -add file to save client user name and password
    -make a better ui
v4.0:
    -make a graphical ui

please keep this header in further editing
"""

import socket
import threading
information = []    # main multidimensional list
# constants are capitalized, those are the addresses in the main list above
CONNECTION = 2
ADDRESS = 3
USER = 0
PASSWORD = 1
clients_num = 0
# the one and only socket configuration
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 5432
s.bind((host, port))
# recommended is 160 clients
s.listen(20)


def byte_to_string(bytes_):
    bytes_ = str(bytes_)
    return bytes_[2:len(bytes_) - 1]    # converts from "b'string_passed'" to "string_passed"


def client_to_client(client1, client2):  # allows client1 to send messages to client2
    while True:
        try:
            data_received = information[client1][CONNECTION].recv(1024)
            if byte_to_string(data_received) == "/exit/":
                threading.Thread(target=client_taking, args=([client1])).start()
                information[client2][CONNECTION].send(str.encode(information[client2][USER] +
                                                                 " left the conversation"))
                threading.Thread(target=client_taking, args=([client2])).start()
                break
            information[client2][CONNECTION].send(data_received)
        except ConnectionResetError:
            try:
                information[client2][CONNECTION].send(str.encode(information[client1][USER] +
                                                                 " is disconnected and left the conversation"))
                threading.Thread(target=client_taking, args=([client2])).start()
                break
            except ConnectionResetError:
                break
    return True


def client_taking(client_num):  # executes after successful login or signup
    while True:
        try:
            information[client_num][CONNECTION].send(b"type '/exit/' to break the connection with the server")
            information[client_num][CONNECTION].send(b"type 1 to connect to a client")
            information[client_num][CONNECTION].send(b"type 2 to check for incoming clients")
            information[client_num][CONNECTION].send(b"type 3 to remain idle or text when a user accepts your request")
            data_rcv = information[client_num][CONNECTION].recv(1024)
            if byte_to_string(data_rcv) == "1":
                information[client_num][CONNECTION].send(b"type the username of the person you want to talk to: ")
                username_to_talk_to = information[client_num][CONNECTION].recv(1024)
                client_num2 = check_client(byte_to_string(username_to_talk_to))
                information[client_num2].append(information[client_num][USER])
                continue
            elif byte_to_string(data_rcv) == "2":
                requests = check_for_text_requests(client_num)
                if requests == "":
                    information[client_num][CONNECTION].send(b"no incoming requests")
                    continue
                else:
                    information[client_num][CONNECTION].send(str.encode(requests + " are requesting to talk with you"))
                    information[client_num][CONNECTION].send(str.encode("type the username you want to accept"))
                    accepted_client_user_name = byte_to_string(information[client_num][CONNECTION].recv(1024))
                    accepted_client_user_num = check_client(accepted_client_user_name)
                    information[accepted_client_user_num][CONNECTION].send(str.encode(information[client_num][USER]
                                                                                      + " accepted your request"))
                    threading.Thread(target=client_to_client, args=([accepted_client_user_num, client_num])).start()
                    threading.Thread(target=client_to_client, args=([client_num, accepted_client_user_num])).start()
                return True
            elif byte_to_string(data_rcv) == "3":
                break
        except ConnectionResetError:
            return False
    return True


def check_for_text_requests(user_num):  # no idea why this worked. ha ha ha
    global i
    users_requests = []
    i = 4
    while True:
        try:
            users_requests.append(information[user_num][i])
            i = i + 1
        except IndexError:
            return_val = ""
            if i != 4:
                for x in range(3, i - 1):
                    return_val = return_val + ", " + str(users_requests[x - 3])
            return return_val.lstrip(", ").rstrip(", ")


def check_client(user_name):    # returns the index num associated with the user_name passed.
    for _i in range(0, clients_num):
        if information[_i][USER] == user_name:
            print(_i)
            return _i
    return "available to add"


def connect_to_client():    # executes when a client connects to the server
    global information, clients_num
    c, addr = s.accept()
    try:
        print('Got connection from', addr)
        threading.Thread(target=connect_to_client, args=()).start()  # to keep the server available to connect to
        c.send(b"type 1 to signup and 2 to login")
        recv = byte_to_string(c.recv(1024))
        if recv == "1":
            def sign_up():
                global clients_num, information
                c.send(b"type your user name: ")
                user_name = byte_to_string(c.recv(1024))
                c.send(b"type your password: ")
                passw = byte_to_string(c.recv(1024))
                if str(check_client(user_name)) == "available to add":
                    information.append([user_name, passw, c, addr])  # this is the initialization of a client
                    clients_num = clients_num + 1
                    t = threading.Thread(target=client_taking, args=([clients_num - 1]))
                    t.setName(user_name)
                    t.start()
                    return True
                else:
                    c.send(b"user name taken, pls choose another one")
                    return False
            while not sign_up():
                continue
            return True
        elif recv == "2":
            def login():
                global information
                c.send(b"type your user name: ")
                user_name = byte_to_string(c.recv(1024))
                c.send(b"type your password: ")
                passw = byte_to_string(c.recv(1024))
                user_num = login_operation(user_name, passw)
                if str(user_num).isdigit():
                    information[user_num][CONNECTION] = c
                    information[user_num][ADDRESS] = addr
                    c.send(b"logged in successfully")
                    t = threading.Thread(target=client_taking, args=([user_num]))   # transfers client to the main function
                    t.setName(user_name)
                    t.start()
                    return True
                else:
                    c.send(b"login failed")
                    threading.Thread(target=login, args=()).start()
                    return True
            login()
        else:
            c.send(b"invalid input, pls stick to instructions")
        print(threading.activeCount())  # this is unnecessary
        return True
    except ConnectionResetError:
        return True


def login_operation(user_name, password):
    user_num = check_client(user_name)
    if str(user_num).isdigit():
        if information[user_num][PASSWORD] == password:
            return user_num
        else:
            return "wrong password"
    else:
        return "available"


if __name__ == '__main__':
    connection_thread = threading.Thread(target=connect_to_client, args=())
    connection_thread.start()
    print("server launched successfully")

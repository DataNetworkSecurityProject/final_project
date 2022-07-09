import sys
import os

sys.path.append("..")
sys.path.append("../server")

import client_utils

import server.api

SERVER_PUB_KEY_PATH = "../server/pub.key"  # It should be in the client side but we do this to be simpler.


def main():
    server_pub_key = client_utils.load_server_pub_key(SERVER_PUB_KEY_PATH)

    print("Welcome to your Secure File System!")

    client = None

    valid_input = False
    while valid_input is False:
        print("1: Sing-in")
        print("2: Sign-up")
        user_input = input("Enter your choice (`exit` for exit from the program): ")
        if user_input == 'exit':
            raise SystemExit
        elif user_input == '1':
            handle_sign_in()
            valid_input = True
        elif user_input == '2':
            client = handle_sign_up(server_pub_key)
            if client is not None:  # TODO in None situation, database is get locked! (sqlite3.OperationalError: database is locked)
                valid_input = True
        else:
            print("Invalid input. Try again...")

    handle_client_commands(client)


def handle_sign_in():
    pass  # TODO


def handle_sign_up(server_pub_key):
    client_keys = None

    valid_input = False
    while valid_input is False:
        print("1: Load your RSA key pair from the disk")
        print("2: Generate a new RSA key pair")
        user_input = input("Enter your choice (`exit` for exit from the program): ")
        if user_input == 'exit':
            raise SystemExit
        elif user_input == '1':
            valid_input = True
            client_keys = handle_load_key_pair()
        elif user_input == '2':
            valid_input = True
            client_keys = handle_generate_key_pair()
        else:
            print("Invalid input. Try again...")

    client = Client(client_keys)

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    client.username = username
    client.session_key = client_utils.generate_session_key()

    # First encrypt password with session key, then sign it with client private key
    encrypted_password, nonce, tag = client_utils.symmetric_encrypt(client.session_key, password)
    password_signature = client_utils.asymmetric_sign(client.client_keys.prv_key, encrypted_password)

    # Also encrypt session key with server public key
    encrypted_session_key = client_utils.asymmetric_encrypt(server_pub_key, client.session_key)

    msg, err = server.api.sign_up_user(username, encrypted_password, nonce, tag, password_signature, encrypted_session_key,
                                       client.client_keys.pub_key)
    print(msg)
    if err is not None:
        print(err)
        return None

    client.current_path = "/" + client.username
    return client


def handle_load_key_pair():
    user_input = input("Enter you private key path to load (default is `./prv.key`): ")
    if user_input == "":
        user_input = "./prv.key"
    prv_key = client_utils.load_key(user_input)
    pub_key = client_utils.get_pub_key(prv_key)
    client_keys = ClientKeys(prv_key, pub_key)
    return client_keys


def handle_generate_key_pair():
    user_input = input("Enter a directory path to save your private and public keys (`.` for current directory): ")
    if user_input == 'exit':
        raise SystemExit
    else:
        prv_key, pub_key = client_utils.generate_RSA_key_pair()
        prv_key_path, pub_key_path = client_utils.save_key_pair(prv_key, pub_key, path=user_input)
        print("Private key generated in " + prv_key_path)
        print("Public key generated in " + pub_key_path)
        client_keys = ClientKeys(prv_key, pub_key)
        return client_keys


def handle_client_commands(client):
    while True:
        current_path = client.current_path
        if current_path == "/" + client.username:
            current_path = "~"
        user_command = input(client.username + ":" + current_path + "$ ")
        command = user_command.split(" ")[0]

        if command == "exit":
            raise SystemExit
        elif command == "mkdir":
            if len(user_command.split(" ")) != 2:
                print("command ls gets only 1 argument")
                continue

            path = user_command.split(" ")[1]
            if not path.startswith("/"):
                path = os.path.join(client.current_path, path)
            final_command = "mkdir " + path
            encrypted_command, nonce, tag = client_utils.symmetric_encrypt(client.session_key, final_command)
            response, err = server.api.user_command(client.username, encrypted_command, nonce, tag)
            if err is not None:
                print(response)
                print(err)
        elif command == "touch":
            pass  # TODO
        elif command == "cd":
            pass  # TODO
        elif command == "ls":
            pass  # TODO
        elif command == "rm":
            pass  # TODO
        elif command == "mv":
            pass  # TODO
        elif command == "share":
            pass  # TODO
        elif command == "revoke":
            pass  # TODO
        else:
            print("command " + command + " not found")


class Client:
    username = None
    session_key = None
    current_path = None

    def __init__(self, client_keys):
        self.client_keys = client_keys


class ClientKeys:
    def __init__(self, prv_key, pub_key):
        self.prv_key = prv_key
        self.pub_key = pub_key


if __name__ == "__main__":
    main()

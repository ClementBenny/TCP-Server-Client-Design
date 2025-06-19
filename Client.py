import socket
import threading
import struct

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.received_messages = []

    def connect_to_server(self):
        ip = input("Enter Server IP: ")
        port = int(input("Enter Port: "))
        try:
            self.socket.connect((ip, port))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            print("Connected to server.")
            self.menu()
        except:
            print("[!] Connection failed.")

    def send_message_to_server(self):
        msg = input("Enter message: ")
        self.send_message_raw(msg)
        print("Message sent to server.")

    def receive_messages(self):
        while self.running:
            try:
                msg = self.receive_message()
                if msg:
                    self.received_messages.append(msg)
                    print(f"\n[Server]: {msg}")
                else:
                    break
            except:
                break
        self.socket.close()

    def view_server_messages(self):
        print("\n--- Messages from Server ---")
        if not self.received_messages:
            print("No messages received yet.")
        else:
            for i, msg in enumerate(self.received_messages, 1):
                print(f"{i}. {msg}")

    def send_message_raw(self, msg):
        msg_bytes = msg.encode('utf-8')
        msg_len = struct.pack('>I', len(msg_bytes))
        self.socket.sendall(msg_len + msg_bytes)

    def receive_message(self):
        raw_len = self._recv_all(4)
        if not raw_len:
            return None
        msg_len = struct.unpack('>I', raw_len)[0]
        msg_bytes = self._recv_all(msg_len)
        return msg_bytes.decode('utf-8') if msg_bytes else None

    def _recv_all(self, n):
        data = b''
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def menu(self):
        while self.running:
            print("\n--- Client Menu ---")
            print("1. Send Message to Server")
            print("2. View Messages from Server")
            print("3. Disconnect and Exit")
            choice = input("Enter choice: ")
            if choice == '1':
                self.send_message_to_server()
            elif choice == '2':
                self.view_server_messages()
            elif choice == '3':
                confirm = input("Are you sure you want to disconnect? (y/n): ")
                if confirm.lower() == 'y':
                    self.running = False
                    print("Disconnected from server. Exiting...")
                    self.socket.close()
                    break
            else:
                print("[!] Invalid choice.")

if __name__ == "__main__":
    Client().connect_to_server()

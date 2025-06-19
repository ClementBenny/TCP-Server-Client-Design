import socket
import threading
import datetime
import struct

class Server:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {client_id: {'socket': sock, 'address': addr, 'connected_at': time}}
        self.messages = []  # [(timestamp, client_id, message)]
        self.running = True

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"[+] Server started on {self.host}:{self.port}")
        threading.Thread(target=self.accept_connections, daemon=True).start()
        self.menu()

    def accept_connections(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                client_id = f"C{100 + len(self.clients) + 1}"
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.clients[client_id] = {
                    'socket': client_socket,
                    'address': addr,
                    'connected_at': timestamp
                }
                self.send_message_raw(client_socket, f"Connected to server as Client ID: {client_id}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_id), daemon=True).start()
                print(f"\n[+] {client_id} connected from {addr}")
            except Exception as e:
                print(f"[!] Error accepting connection: {e}")

    def handle_client(self, sock, client_id):
        while self.running:
            try:
                msg = self.receive_message(sock)
                if msg:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.messages.append((timestamp, client_id, msg))
                    print(f"[{timestamp}] {client_id}: {msg}")
                else:
                    break
            except:
                break
        print(f"[-] {client_id} disconnected")
        sock.close()
        if client_id in self.clients:
            del self.clients[client_id]

    def view_connected_clients(self):
        print("\n--- Connected Clients ---")
        if(len(self.clients) == 0):
            print("\nNo connected clients. ")
        for cid, info in self.clients.items():
            print(f"ID: {cid} | Address: {info['address'][0]} | Connected: {info['connected_at']}")

    def send_message_to_all(self):
        msg = input("Enter message to broadcast: ")
        for cid, info in self.clients.items():
            try:
                self.send_message_raw(info['socket'], f"Server: {msg}")
            except:
                print(f"[!] Failed to send to {cid}")
        print(f"Message sent to {len(self.clients)} clients.")

    def send_message_to_client(self):
        cid = input("Enter Client ID: ")
        if cid in self.clients:
            msg = input("Enter Message: ")
            try:
                self.send_message_raw(self.clients[cid]['socket'], f"Server: {msg}")
                print(f"Message sent to {cid}.")
            except:
                print("[!] Failed to send message.")
        else:
            print("[!] Client ID not found.")

    def view_client_messages(self):
        cid = input("Enter Client ID (or 'all' to view all): ")
        print("\n--- Client Messages ---")
        for timestamp, client_id, msg in self.messages:
            if cid == "all" or client_id == cid:
                print(f"[{timestamp}] {client_id}: {msg}")

    def stop_server(self):
        self.running = False
        for info in self.clients.values():
            info['socket'].close()
        self.server_socket.close()
        print("Server shutting down...")

    def send_message_raw(self, sock, msg):
        msg_bytes = msg.encode('utf-8')
        msg_len = struct.pack('>I', len(msg_bytes))
        sock.sendall(msg_len + msg_bytes)

    def receive_message(self, sock):
        raw_len = self._recv_all(sock, 4)
        if not raw_len:
            return None
        msg_len = struct.unpack('>I', raw_len)[0]
        msg_bytes = self._recv_all(sock, msg_len)
        return msg_bytes.decode('utf-8') if msg_bytes else None

    def _recv_all(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def menu(self):
        while self.running:
            print("\n--- Server Menu ---")
            print("1. View Connected Clients")
            print("2. Send Message to All Clients")
            print("3. Send Message to Specific Client")
            print("4. View Messages from Clients")
            print("5. Stop Server and Exit")
            choice = input("Enter choice: ")
            if choice == '1':
                self.view_connected_clients()
            elif choice == '2':
                self.send_message_to_all()
            elif choice == '3':
                self.send_message_to_client()
            elif choice == '4':
                self.view_client_messages()
            elif choice == '5':
                confirm = input("Are you sure? (y/n): ")
                if confirm.lower() == 'y':
                    self.stop_server()
                    break
            else:
                print("[!] Invalid choice.")

if __name__ == "__main__":
    Server().start_server()

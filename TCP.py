import os
import socket


LITTLE = "little"
UTF8 = "utf8"


class TCP(socket.socket):
    CHUNKSIZE = 1024

    def __init__(self: socket.socket):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def recv_all(self: socket.socket, size: int) -> bytes:
        return self.recv(size, socket.MSG_WAITALL)

    def send_int(self: socket.socket, value: int, size: int, signed: bool) -> None:
        self.sendall(value.to_bytes(size, LITTLE, signed=signed))

    def recv_int(self: socket.socket, size: int, signed: bool) -> int:
        return int.from_bytes(TCP.recv_all(self, size), LITTLE, signed=signed)

    def recv_byte(self: socket.socket) -> int:
        return TCP.recv_int(self, 1, False)

    def recv_ushort(self: socket.socket) -> int:
        return TCP.recv_int(self, 2, False)

    def send_bool(self: socket.socket, value: bool) -> None:
        TCP.send_int(self, 1 if value else 0, 1, False)

    def recv_bool(self: socket.socket) -> bool:
        return TCP.recv_int(self, 1, False) == 1

    def send_str(self: socket.socket, text: str) -> None:
        encoded = text.encode(UTF8)
        TCP.send_int(self, len(encoded), 2, False)
        self.sendall(encoded)

    def recv_str(self: socket.socket) -> str:
        length = TCP.recv_int(self, 2, False)
        return TCP.recv_all(self, length).decode(UTF8)

    def send_nostr(self: socket.socket) -> None:
        TCP.send_int(self, 0, 2, False)

    def send_file(self: socket.socket, path: str, log: bool) -> None:
        file_size = os.path.getsize(path)
        if log:
            print(" - outcoming file:", path, "(size:", file_size, "bytes)")
        TCP.send_int(self, file_size, 4, False)
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(TCP.CHUNKSIZE)
                size = len(chunk)
                if size > 0:
                    self.sendall(chunk)
                else:
                    break
        if log:
            print(" - outcoming file:", path, "(success)")

    def recv_file(self: socket.socket, path: str, log: bool) -> None:
        file_size = TCP.recv_int(self, 4, False)
        if log:
            print(" - incoming file:", path, "(size:", file_size, "bytes)")
        with open(path, 'wb') as file:
            while file_size > 0:
                recv_size = TCP.CHUNKSIZE if file_size > TCP.CHUNKSIZE else file_size
                if recv_size > 0:
                    file.write(TCP.recv_all(self, recv_size))
                    file_size -= recv_size
                else:
                    break
        if log:
            print(" - incoming file:", path, "(success)")

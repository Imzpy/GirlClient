import socket
import base64

STARTFLAG = b'\x01'
ENDFLAG = b'\x02'
BUFFER_SIZE = 8192

class TcpClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = None
        self.recv_buffer = bytearray()

    def connect(self):
        try:
            self.sock = socket.create_connection((self.host, self.port))
            self.sock.settimeout(0.1)
            print(f"[+] 已连接到服务器 {self.host}:{self.port}")
        except Exception as e:
            print(f"[!] 连接失败: {e}")
            return False
        return True

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("[*] 连接已关闭")

    def encode_base64(self, text: str) -> bytes:
        return base64.b64encode(text.encode())

    def decode_base64(self, data: bytes) -> str:
        return base64.b64decode(data).decode(errors='ignore')

    def build_packet(self, data: str) -> bytes:
        return STARTFLAG + self.encode_base64(data) + ENDFLAG

    def send(self, text: str) -> bool:
        if not self.sock:
            print("[!] 未连接服务器")
            return False
        try:
            packet = self.build_packet(text)
            self.sock.sendall(packet)
            print(f"[>] 发送: {text}")
            return True
        except Exception as e:
            print(f"[!] 发送失败: {e}")
            return False

    def receive(self) -> list[str]:
        """从 socket 接收数据并返回完整的包（已解码）"""
        if not self.sock:
            return []
        try:
            data = self.sock.recv(BUFFER_SIZE)
            if data:
                self.recv_buffer.extend(data)
        except socket.timeout:
            pass  # 没有数据，跳过
        except Exception as e:
            print(f"[!] 接收失败: {e}")
            return []

        return self._extract_packets()

    def _extract_packets(self) -> list[str]:
        packets = []
        while True:
            start = self.recv_buffer.find(STARTFLAG)
            end = self.recv_buffer.find(ENDFLAG, start + 1)
            if start != -1 and end != -1 and end > start:
                b64_data = self.recv_buffer[start + 1:end]
                try:
                    decoded = self.decode_base64(b64_data)
                    packets.append(decoded)
                except Exception as e:
                    print(f"[!] 解码失败: {e}")
                del self.recv_buffer[:end + 1]
            else:
                break
        return packets

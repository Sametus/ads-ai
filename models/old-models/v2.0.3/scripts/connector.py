import socket
import json
import struct

"""
UNİTY -> PYTHON : JSON-DIST YAPISI:
    {
        episode_id:
        step_id:
        states:
        {
            target_dir : [x,y,z],
            rel_vel : [x,y,z],
            roc_vel: [x,y,z],
            roc_ang_vel: [x,y,z],
            roc_h: rh,
            target_h: t_h,
            g : [x,y,z],
            distance : d,
            closing_rate: cr,
            blend_w: bw
        }
    }
"""

class Connector:
    
    def __init__(self,ip,port):
        # Bağlantı Kurma

        # 1- TCP Bağlantısı Oluştur
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # OPSİYONEL: Gecikme Azaltıcı:
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # 2- Bağlanma
        self.sock.connect((self.ip, self.port))

    def send_packet(self,data:dict):
        
        # Paket Dönüşümü, Yollama ve Fraiming Kontrolü
        # List -> JSON
        # JSON --> C#

        # 1- Dict -> Json -> bytes
        json_str = json.dumps(data, separators=(",",":"), ensure_ascii=False)
        payload = json_str.encode("utf-8")

        # 2- 4-bytes Length Prefix (big-endian unsigned int)
        header = struct.pack(">I",len(payload))

        # 3- Gönder
        self.sock.sendall(header + payload)

    def read_packet(self) -> dict:
        
        # Paket Okuma, Dönüşümü ve Fraiming Kontrolü
        # C# --> Python
        # JSON -> List
        
        # 1- 4-bytes Header Okuma
        header = self._recv_exact(4)
        msg_len = struct.unpack(">I",header)[0]

        # 2- Payload Okuma
        payload = self._recv_exact(msg_len)

        # 3- bytes -> Json -> dict
        json_str = payload.decode("utf-8")
        data = json.loads(json_str)
        return data
    
    def _recv_exact(self, n:int) -> bytes:

        # Soketten tam olarak n byte gelene kadar okur. TCP stream olduğu için tek recv yeterli olmaz.

        chunks = []
        received = 0

        while received < n:
            chunk = self.sock.recv(n-received)

            if chunk == b"":
                raise ConnectionError("Socket connection closed while receiving data.")
            chunks.append(chunk)
            received += len(chunk)
        
        return b"".join(chunks)
    
    def close(self):
        
        # Bağlantı Kapatma
        self.sock.close()


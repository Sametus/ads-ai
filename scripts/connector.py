import json
import socket
import struct

"""
UNITY -> PYTHON packet schema:
    {
        "episode_id": int,
        "step_id": int,
        "states": {
            "distance": float,
            "look_angle_rad": float,
            "closing_speed": float,
            "rel_vel": [x, y, z],
            "roc_ang_vel": [x, y, z],
            "g": [x, y, z],
            "agl": float,
            "alt_error": float,
            "grounded_flag": float
        },
        "telemetry": {
            "rocket_pos_world": [x, y, z],
            "rocket_euler_world": [x, y, z],
            "rocket_rot_world": [x, y, z, w],
            "rocket_point_pos_world": [x, y, z],
            "rocket_point_forward_world": [x, y, z],
            "rocket_point_up_world": [x, y, z],
            "rocket_vel_world": [x, y, z],
            "rocket_vel_local": [x, y, z],
            "rocket_ang_vel_world": [x, y, z],
            "rocket_ang_vel_local": [x, y, z],
            "target_pos_world": [x, y, z],
            "target_euler_world": [x, y, z],
            "target_rot_world": [x, y, z, w],
            "target_point_pos_world": [x, y, z],
            "target_point_forward_world": [x, y, z],
            "target_point_up_world": [x, y, z],
            "target_vel_world": [x, y, z],
            "target_vel_in_rocket_local": [x, y, z],
            "target_ang_vel_world": [x, y, z],
            "target_ang_vel_in_rocket_local": [x, y, z],
            "rel_pos_world": [x, y, z],
            "rel_pos_local": [x, y, z],
            "rel_dir_world": [x, y, z],
            "rel_dir_local": [x, y, z],
            "rel_vel_world": [x, y, z],
            "rel_vel_local": [x, y, z],
            "gravity_world": [x, y, z],
            "gravity_local": [x, y, z],
            "target_speed": float
        }
    }
"""


class Connector:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect((self.ip, self.port))

    def send_packet(self, data: dict):
        json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        payload = json_str.encode("utf-8")
        header = struct.pack(">I", len(payload))
        self.sock.sendall(header + payload)

    def read_packet(self) -> dict:
        header = self._recv_exact(4)
        msg_len = struct.unpack(">I", header)[0]
        payload = self._recv_exact(msg_len)

        json_str = payload.decode("utf-8")
        data = json.loads(json_str)
        return data

    def _recv_exact(self, n: int) -> bytes:
        chunks = []
        received = 0

        while received < n:
            chunk = self.sock.recv(n - received)
            if chunk == b"":
                raise ConnectionError("Socket connection closed while receiving data.")
            chunks.append(chunk)
            received += len(chunk)

        return b"".join(chunks)

    def close(self):
        self.sock.close()

from __future__ import annotations

import json
import socket
import threading


HOST = "0.0.0.0"
PORT = 12345


def receive_loop(conn: socket.socket) -> None:
    buffer = ""
    while True:
        data = conn.recv(4096)
        if not data:
            return
        buffer += data.decode("utf-8")
        while "%" in buffer:
            frame, buffer = buffer.split("%", 1)
            if not frame.strip():
                continue
            try:
                payload = json.loads(frame)
                print("[客户端反馈]", json.dumps(payload, ensure_ascii=False))
            except json.JSONDecodeError as exc:
                print("[无效JSON]", exc, repr(frame))


def send_command(conn: socket.socket, stage: str, component: str | None, state: str) -> None:
    params = {"Stage": stage, "State": state}
    if component:
        params["Component"] = component
    payload = {"Cmd": "Measure", "Params": params}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "%"
    conn.sendall(raw.encode("utf-8"))
    print("[发送命令]", raw)


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"测试服务器监听 {HOST}:{PORT}")
        conn, addr = server.accept()
        with conn:
            print("客户端已连接：", addr)
            threading.Thread(target=receive_loop, args=(conn,), daemon=True).start()
            print("输入示例：HTDJ Leg1 Init；SQLW - Move；输入 quit 退出")
            while True:
                line = input("> ").strip()
                if line.lower() == "quit":
                    return
                parts = line.split()
                if len(parts) != 3:
                    print("格式：Stage Component State；无 Component 时填写 -")
                    continue
                stage, component, state = parts
                send_command(conn, stage, None if component == "-" else component, state)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Startup script for running FastAPI and WebSocket servers
"""

import subprocess
import sys
import time
import signal


class ServerManager:
    def __init__(self):
        self.processes = []
        self.running = True

    def signal_handler(self, signum, frame):
        print("\nShutting down servers...")
        self.running = False

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass

        sys.exit(0)

    def start_fastapi_server(self):
        print("Starting FastAPI server on port 8000...")

        process = subprocess.Popen([
            sys.executable,
            "-m",
            "uvicorn",
            "server:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload"
        ])

        self.processes.append(process)
        return process

    def start_websocket_server(self):
        print("Starting WebSocket server on port 5555...")

        process = subprocess.Popen([
            sys.executable,
            "socketServer.py"
        ])

        self.processes.append(process)
        return process

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            # FastAPI
            fastapi_process = self.start_fastapi_server()

            time.sleep(2)

            if fastapi_process.poll() is not None:
                print("Failed to start FastAPI server")
                return

            print("FastAPI server started successfully!")

            # WebSocket
            websocket_process = self.start_websocket_server()

            time.sleep(2)

            if websocket_process.poll() is not None:
                print("Failed to start WebSocket server")
                return

            print("WebSocket server started successfully!")

            print("\nAvailable endpoints:")
            print("  - Health check: http://localhost:8000/health")
            print("  - API docs: http://localhost:8000/docs")
            print("  - Main page: http://localhost:8000/")
            print("  - WebSocket: ws://localhost:5555")
            print("  - MCP server: Disabled")

            print("\nServers are running. Press Ctrl+C to stop.")

            while self.running:
                time.sleep(1)

                if fastapi_process.poll() is not None:
                    print("FastAPI server stopped unexpectedly")
                    break

                if websocket_process.poll() is not None:
                    print("WebSocket server stopped unexpectedly")
                    break

        except KeyboardInterrupt:
            pass

        finally:
            self.signal_handler(None, None)


if __name__ == "__main__":
    print("NEPSE API Server Starter")
    print("=" * 25)
    print("Starting NEPSE API servers...\n")

    manager = ServerManager()
    manager.run()
#!/usr/bin/env python
from websockets.sync.server import serve
import config
import utils.hand
import json

def echo(websocket):
    for message in websocket:
        try:
            data = json.loads(message)
            print("Json received:", data)
            
            response = {"status": "ok", "received": data}
            websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            error_response = {"status": "error", "message": "Invalid JSON format"}
            websocket.send(json.dumps(error_response))

def main():
    dealer = utils.hand.Hand()
    player = utils.hand.hand()
    with serve(echo, config.host, config.port) as server:
        print(f"Server running on ws://{config.host}:{config.port}")
        server.serve_forever()

if __name__ == "__main__":
    main()

import asyncio
import websockets
import json
import config

async def start_client():
    uri = f"ws://{config.host}:{config.port}"
    
    # Connect to the WebSocket server
    async with websockets.connect(uri) as websocket:
        print(f"Connected to: {config.host}:{config.port}")
        
        # Start interaction with the server
        await websocket.send(json.dumps({"action": "start"}))

        # Receive the initial hand and dealer's showing card
        message = await websocket.recv()
        print("Message received from server:", message)
        
        try:
            data = json.loads(message)
            print(f"Your hand: {data['player']} (Total: {data['player_total']})")
            print(f"Dealer's showing card: {data['dealer'][0]}")  # Assuming only the first card is shown
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
            return  # Exit if there's a JSON error

        # Player's turn
        while True:
            move = input("Enter 'hit' to draw a card or 'stand' to hold: ").strip().lower()
            
            if move not in ['hit', 'stand']:
                print("Invalid command. Please enter 'hit' or 'stand'.")
                continue

            # Send action to server
            await websocket.send(json.dumps({"action": move}))

            # Receive response from server
            response = await websocket.recv()
            print("Response from server:", response)

            try:
                response_data = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                break  # Exit loop if JSON error

            if "status" in response_data and response_data["status"] == "bust":
                print(response_data["message"])
                break
            elif move == 'stand':
                print(f"Your final total: {response_data['player_total']}")
                print(f"Dealer's hand: {response_data['dealer']} (Total: {response_data['dealer_total']})")
                print(response_data["message"])
                break
            else:
                print(f"Your hand: {response_data['player']} (Total: {response_data['player_total']})")

if __name__ == "__main__":
    asyncio.run(start_client())

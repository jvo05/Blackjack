import socket
import json
import config

# Start the client and connect to the server
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((config.host, config.port))

     # Start interaction with the server
    client.sendall(json.dumps({"action": "start"}).encode())

    # Receive the initial hand and dealer's showing card
    message = client.recv(1024).decode()
    
    if not message:
        print("No data received from the server.")
        client.close()
        return  # Exit if there's no data
    
    try:
        data = json.loads(message)
        print(f"Your hand: {data['player_hand']} (Total: {data['player_total']})")
        print(f"Dealer's showing card: {data['dealer_showing']}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        client.close()
        return  # Exit if there's a JSON error

    # Player's turn
    while True:
        move = input("Enter 'hit' to draw a card or 'stand' to hold: ").strip().lower()
        
        if move not in ['hit', 'stand']:
            print("Invalid command. Please enter 'hit' or 'stand'.")
            continue

        # Send action to server
        client.sendall(json.dumps({"action": move}).encode())

        # Receive response from server
        response = client.recv(1024).decode()

        if not response:
            print("No response from server.")
            break  # Exit loop if no response

        try:
            response_data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            break  # Exit loop if JSON error

        if "status" in response_data and response_data["status"] == "bust":
            print(response_data["result"])
            break
        elif move == 'stand':
            print(f"Your final total: {response_data['player_total']}")
            print(f"Dealer's hand: {response_data['dealer_hand']} (Total: {response_data['dealer_total']})")
            print(response_data["result"])
            break
        else:
            print(f"Your hand: {response_data['player_hand']} (Total: {response_data['player_total']})")

    client.close()

if __name__ == "__main__":
    start_client()
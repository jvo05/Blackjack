import socket
import json

HOST = 'localhost'
PORT = 12345

# Start the client and connect to the server
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Receive the initial hand and dealer's showing card
    message = client.recv(1024).decode()
    data = json.loads(message)
    print(f"Your hand: {data['player_hand']} (Total: {data['player_total']})")
    print(f"Dealer's showing card: {data['dealer_showing']}")

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
        response_data = json.loads(response)

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

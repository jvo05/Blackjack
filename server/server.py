import socket
import threading
import json
import random

# Constants for server
HOST = 'localhost'
PORT = 12345

# Card deck values (10 is repeated for J, Q, K, and 11 is for Ace)
deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

# Function to deal a card
def deal_card():
    return random.choice(deck)

# Function to calculate total hand value, adjusting for Aces
def calculate_hand(hand):
    total = sum(hand)
    aces = hand.count(11)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

# Determine game outcome
def determine_winner(player_total, dealer_total):
    if player_total > 21:
        return "bust"  # Player busts
    elif dealer_total > 21:
        return "win"   # Dealer busts
    elif player_total > dealer_total:
        return "win"   # Player has a higher hand
    elif player_total < dealer_total:
        return "lose"  # Dealer has a higher hand
    else:
        return "tie"   # Both totals are equal

# Handle each client connection
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]  # Dealer also gets two cards initially

    # Send initial hands
    conn.sendall(json.dumps({
        "player_hand": player_hand,
        "dealer_showing": dealer_hand[0],
        "player_total": calculate_hand(player_hand)
    }).encode())

    # Player's turn
    while True:
        try:
            message = conn.recv(1024).decode()
            if not message:
                break
            data = json.loads(message)

            if data['action'] == 'hit':
                player_hand.append(deal_card())
                player_total = calculate_hand(player_hand)
                conn.sendall(json.dumps({
                    "player_hand": player_hand,
                    "player_total": player_total
                }).encode())
                if player_total > 21:
                    conn.sendall(json.dumps({"status": "bust", "result": "You busted! Dealer wins."}).encode())
                    return

            elif data['action'] == 'stand':
                break

        except Exception as e:
            print(f"[ERROR] {e}")
            break

    # Dealer's turn
    dealer_total = calculate_hand(dealer_hand)
    while dealer_total < 17:
        dealer_hand.append(deal_card())
        dealer_total = calculate_hand(dealer_hand)

    # Determine winner
    player_total = calculate_hand(player_hand)
    result = determine_winner(player_total, dealer_total)
    
    if result == "win":
        result_message = "Congratulations! You win!"
    elif result == "lose":
        result_message = "Dealer wins. Better luck next time!"
    else:
        result_message = "It's a tie!"

    # Send final result
    conn.sendall(json.dumps({
        "status": "stand",
        "player_total": player_total,
        "dealer_hand": dealer_hand,
        "dealer_total": dealer_total,
        "result": result_message
    }).encode())
    conn.close()

# Main server function
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("[SERVER STARTED] Waiting for connections...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    start_server()

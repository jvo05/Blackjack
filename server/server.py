#!/usr/bin/env python
import json
from websockets import serve
import config
import utils.hand
import asyncio


async def echo(websocket, path):
    # Initialize player and dealer hands for each client session
    player = utils.hand.Hand()
    dealer = utils.hand.Hand()
    
    async for message in websocket:
        try:
            data = json.loads(message)
            print("Json received:", data)

            response = {"status": "ok", "received": data}
            await websocket.send(json.dumps(response))

            if data.get("action") == "stand":
                # Dealer's turn to draw cards
                while dealer.calculate_score() < 17:
                    dealer.add_random_card()

                # Final score calculation
                player_score = player.calculate_score()
                dealer_score = dealer.calculate_score()

                # Determine the winner
                if dealer_score > 21:
                    result = {"status": "win", "message": "Dealer busts! Player wins!"}
                elif player_score > dealer_score:
                    result = {"status": "win", "message": "Player wins!"}
                elif player_score < dealer_score:
                    result = {"status": "lose", "message": "Dealer wins!"}
                else:
                    result = {"status": "push", "message": "It's a tie!"}

                await websocket.send(json.dumps(result))
                break  # End game after stand

            elif data.get("action") == "hit":
                player.add_random_card()
                dealer.add_random_card()

                player_score = player.calculate_score()
                dealer_score = dealer.calculate_score()

                # Check for winning condition
                if player_score == 21:
                    result = {"status": "win", "message": "Player wins with Blackjack!"}
                    await websocket.send(json.dumps(result))
                    break  # End game if player wins
                elif dealer_score == 21:
                    result = {
                        "status": "lose",
                        "message": "Dealer wins with Blackjack!",
                    }
                    await websocket.send(json.dumps(result))
                    break  # End game if dealer wins
                elif player_score > 21:
                    result = {"status": "lose", "message": "Player busts! Dealer wins!"}
                    await websocket.send(json.dumps(result))
                    break  # End game if player busts
                elif dealer_score > 21:
                    result = {"status": "win", "message": "Dealer busts! Player wins!"}
                    await websocket.send(json.dumps(result))
                    break  # End game if dealer busts

        except json.JSONDecodeError:
            error_response = {"status": "error", "message": "Invalid JSON format"}
            await websocket.send(json.dumps(error_response))


async def main():
    async with serve(echo, config.host, config.port):
        print(f"Server running on ws://{config.host}:{config.port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

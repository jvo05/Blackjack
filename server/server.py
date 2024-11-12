#!/usr/bin/env python
import json
from websockets import serve
import config
import utils.hand
import asyncio


async def echo(websocket):
    # Initialize player and dealer hands for each client session
    player = utils.hand.Hand()
    dealer = utils.hand.Hand()
    
    async for message in websocket:
        try:
            data = json.loads(message)
            print("Json received:", data)

            if data.get("action") == "start":
                response = {
                    "player":player.hand,
                    "player_total":player.calculate_score(),
                    "dealer":dealer.hand
                }
                await websocket.send(json.dumps(response))
            elif data.get("action") == "stand":
                # Dealer's turn to draw cards
                while dealer.calculate_score() < 17:
                    dealer.add_random_card()

                # Final score calculation
                player_score = player.calculate_score()
                dealer_score = dealer.calculate_score()

                # Determine the winner
                if dealer_score > 21:
                    result = {
                        "status": "win",
                        "message": "Dealer is over 21! You win!",
                        "player": player.hand,
                        "player_total": player.calculate_score(),
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }
                elif player_score > dealer_score:
                    result = {
                        "status": "win",
                        "message": "You win!",
                        "player": player.hand,
                        "player_total": player.calculate_score(),
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }
                elif player_score < dealer_score:
                    result = {
                        "status": "lose",
                        "message": "Dealer wins!",
                        "player": player.hand,
                        "player_total": player.calculate_score(),
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }
                else:
                    result = {
                        "status": "push",
                        "message": "It's a tie!",
                        "player": player.hand,
                        "player_total": player.calculate_score(),
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }

                await websocket.send(json.dumps(result))
                break  # End game after stand

            elif data.get("action") == "hit":
                player.add_random_card()
                dealer.add_random_card()

                player_score = player.calculate_score()
                dealer_score = dealer.calculate_score()

                # Check for winning condition
                if player_score == 21:
                    result = {
                        "status": "win",
                        "message": "You win with Blackjack!",
                        "player": player.hand,
                        "player_total": player_score,
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }
                    await websocket.send(json.dumps(result))
                elif dealer_score == 21:
                    result = {
                        "status": "bust",
                        "message": "Dealer wins with Blackjack!",
                        "player": player.hand,
                        "player_total": player_score,
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }
                    await websocket.send(json.dumps(result))
                elif player_score > 21:
                    result = {
                        "status": "bust",
                        "message": "You are over 21! Dealer wins!",
                        "player": player.hand,
                        "player_total": player_score,
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }
                    await websocket.send(json.dumps(result))
                elif dealer_score > 21:
                    result = {
                        "status": "win",
                        "message": "Dealer is over 21! You win!",
                        "player": player.hand,
                        "player_total": player_score,
                        "dealer": dealer.hand,
                        "dealer_total": dealer_score
                    }
                    await websocket.send(json.dumps(result))

                # If no winning condition is met, send the current hands and scores
                result = {
                    "status": "continue",
                    "player": player.hand,
                    "player_total": player_score,
                    "dealer": dealer.hand,
                    "dealer_total": dealer_score
                }
                await websocket.send(json.dumps(result))


        except json.JSONDecodeError:
            error_response = {"status": "error", "message": "Invalid JSON format"}
            await websocket.send(json.dumps(error_response))


async def main():
    async with serve(echo, config.host, config.port):
        print(f"Server running on ws://{config.host}:{config.port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

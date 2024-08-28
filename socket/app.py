import asyncio
import json
import random
import uuid
from configparser import ConfigParser

import psycopg2
import websockets

from Card import Card, Rank
from CardCollection import CardCollection
from Game import Game
from GamePhaseDeck import GamePhaseDeck
from Player import Player
from RE import RE
from User import User

DEBUG = False

connected = set()
socket_to_player_id = {}

DEFAULT_PHASE_LIST = [
    "S3+S3",
    "S3+R4",
    "S4+R4",
    "R7",
    "R8",
    "R9",
    "S4+S4",
    "C7",
    "S5+S2",
    "S5+S3",
]

INITIAL_HAND_SIZE = 10

parser = ConfigParser()
config = {}

parser.read('database.ini')
if parser.has_section('postgresql'):
    for param in parser.items('postgresql'):
        config[param[0]] = param[1]
else:
    raise Exception(f"No postgresql section in database.ini!")

conn = psycopg2.connect(**config)

cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS public.users (
        id uuid NOT NULL,
        "name" text NOT NULL,
        "token" text NOT NULL,
        created_at timestamp NOT NULL,
        updated_at timestamp NOT NULL,
        CONSTRAINT users_pk PRIMARY KEY (id)
    );
    CREATE UNIQUE INDEX IF NOT EXISTS users_name_idx ON public.users ("name");
    """
)
cur.execute("""
CREATE TABLE IF NOT EXISTS public.games (
    id uuid NOT NULL,
    phase_list json NOT NULL,
    deck json NOT NULL,
    "discard" json NOT NULL,
    current_player uuid NOT NULL,
    host uuid NOT NULL,
    in_progress boolean DEFAULT false NOT NULL,
    winner uuid DEFAULT NULL NULL,
    created_at timestamp NOT NULL,
    updated_at timestamp NOT NULL,
    CONSTRAINT games_pk PRIMARY KEY (id),
    CONSTRAINT games_users_fk FOREIGN KEY (current_player) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT games_users_fk_1 FOREIGN KEY (host) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT games_users_fk_2 FOREIGN KEY (winner) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

""")
cur.execute("""
CREATE TABLE IF NOT EXISTS public.players (
    id uuid NOT NULL,
    game_id uuid NOT NULL,
    user_id uuid NOT NULL,
    hand json NOT NULL,
    turn_index serial NOT NULL,
    phase_index int NOT NULL,
    drew_card boolean DEFAULT false NOT NULL,
    completed_phase boolean DEFAULT false NOT NULL,
    skip_cards json NOT NULL,
    created_at timestamp NOT NULL,
    updated_at timestamp NOT NULL,
    CONSTRAINT players_pk PRIMARY KEY (id),
    CONSTRAINT players_games_fk FOREIGN KEY (game_id) REFERENCES public.games(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT players_users_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS players_game_id_user_id_idx ON public.players (game_id,user_id);
CREATE UNIQUE INDEX IF NOT EXISTS players_game_id_turn_index_idx ON public.players (game_id,turn_index);

""")
cur.execute("""
CREATE TABLE IF NOT EXISTS public.gamephasedecks (
    id uuid NOT NULL,
    game_id uuid NOT NULL,
    phase text NOT NULL,
    deck json NOT NULL,
    created_at timestamp NOT NULL,
    updated_at timestamp NOT NULL,
    CONSTRAINT gamephasedecks_pk PRIMARY KEY (id),
    CONSTRAINT gamephasedecks_games_fk FOREIGN KEY (game_id) REFERENCES public.games(id) ON DELETE CASCADE ON UPDATE CASCADE
);

""")

cur.execute("""

CREATE OR REPLACE VIEW public.players_with_names
AS SELECT u.name,
    p.game_id,
    p.hand,
    p.turn_index,
    p.phase_index,
    p.skip_cards,
    p.drew_card,
    p.completed_phase
   FROM players p
     JOIN users u ON p.user_id = u.id
  ORDER BY p.game_id, p.turn_index;

CREATE OR REPLACE VIEW public.completed_games AS select g.id, u."name" as "current player", g.phase_list, g.deck,
g."discard", u2."name" as "host", g.in_progress, u3.name as "winner" from games g join users u on
g.current_player =u.id join users u2 on u2.id = g.host join users u3 on g.winner = u3.id;


CREATE OR REPLACE VIEW public.noncompleted_games AS select g.id, u."name" as "current player", g.phase_list, g.deck,
g."discard", u2."name" as "host", g.in_progress, g.winner from games g join users u on g.current_player = u.id join
users u2 on u2.id = g.host where g.winner is null;

  """)

conn.commit()

User.set_cursor(cur)
Game.set_cursor(cur)
Player.set_cursor(cur)
GamePhaseDeck.set_cursor(cur)


async def send_users():
    user_list = User.all()
    websockets.broadcast(connected, json.dumps({"type": "get_users", "users": [u.to_json_dict() for u in user_list]}))


async def send_players():
    socket_to_delete = set()
    for (socket, player_id) in socket_to_player_id.items():
        
        # This player is deleted
        # We'll need to send a different player to this socket
        
        if not Player.exists(player_id):
            socket_to_delete.add(socket)
            break
        
        player = Player.get_by_id(player_id)
        game = Game.get_by_id(player.game_id)
        user_id = player.user_id
        game_id = game.id
        player_dict = player.to_json_dict()
        if player.phase_index < len(game.phase_list):
            player_dict["phase"] = game.phase_list[player.phase_index]
        else:
            player_dict["phase"] = "WINNER"
        
        await socket.send(json.dumps(
            {
                "type": "get_player",
                "game_id": str(game_id),
                "user_id": str(user_id),
                "player": player_dict,
            }
        ))
        game_dict = Game.get_by_id(game_id).to_json_dict()
        
        # Don't send the entire deck
        if "deck" in game_dict:
            del game_dict["deck"]
        
        game_dict["players"] = []
        game_dict["users"] = []
        
        player_list = [player for player in Player.all() if player.game_id == game.id]
        player_list.sort(key=lambda p: p.turn_index)
        for player in player_list:
            user_dict = User.get_by_id(player.user_id).to_json_dict()
            player_dict = player.to_json_dict()
            player_dict["name"] = User.get_by_id(player.user_id).name
            player_dict["hand_size"] = len(player.hand)
            
            if "hand" in player_dict:
                del player_dict["hand"]
            
            if "token" in user_dict:
                del user_dict["token"]
            
            game_dict["players"].append(player_dict)
            game_dict["users"].append(user_dict)
        
        game_dict["phase_decks"] = [x.to_json_dict() for x in GamePhaseDeck.all_where_game_id(str(game.id))]
        
        await socket.send(json.dumps(
            {
                "type": "get_game",
                "game": game_dict
            }
        ))


async def send_games():
    game_list = []
    for game in Game.all():
        game_dict = game.to_json_dict()
        if "deck" in game_dict:
            del game_dict["deck"]
        if "discard" in game_dict:
            del game_dict["discard"]
        
        game_dict["users"] = []
        cur.execute(
            "SELECT users.id FROM users JOIN players ON users.id = players.user_id JOIN games "
            "ON players.game_id = games.id WHERE games.id = %s",
            (str(game.id),)
        )
        user_id_list = list(cur.fetchall())
        
        for (user_id,) in user_id_list:
            user_dict = User.get_by_id(user_id).to_json_dict()
            if "token" in user_dict:
                del user_dict["token"]
            game_dict["users"].append(user_dict)
        
        game_list.append(game_dict)
    
    websockets.broadcast(
        connected, json.dumps({"type": "get_games", "games": game_list})
    )


def create_game(data):
    user_id = data["user_id"]
    if not User.exists(user_id):
        return json.dumps(
            {
                "type": "rejection",
                "message": f"User ID {user_id} is not valid!",
            }
        )
    else:
        try:
            g = Game(phase_list=DEFAULT_PHASE_LIST, deck=CardCollection(), discard=CardCollection(), host=user_id,
                     current_player=user_id, in_progress=False)
            g.save()
            
            p = Player(game_id=g.id, user_id=user_id)
            p.save()
            conn.commit()
            # For each game, let's also list the players who are in it
            game_dict = g.to_json_dict()
            game_dict["users"] = [User.get_by_id(user_id).to_json_dict()]
            
            return json.dumps({"type": "create_game", "game": game_dict})
        
        except Exception:
            return json.dumps({"type": "rejection", "message": "Cannot create game"})


def player_action(data):
    player_id = data["player_id"]
    
    player = Player.get_by_id(player_id)
    game_id = player.game_id
    user_id = player.user_id
    
    hand = player.hand
    game = Game.get_by_id(game_id)
    
    complete_turn = False
    
    # Players are always allowed to sort their cards
    # Any other action requires you to wait until your turn
    is_sorting = False
    if data["action"] == "sort_by_color":
        hand.sort(key=lambda x: x.color.value)
        player.save()
        conn.commit()
        is_sorting = True
    elif data["action"] == "sort_by_rank":
        hand.sort(key=lambda x: x.rank.value)
        player.save()
        conn.commit()
        is_sorting = True
    elif game.current_player != player.user_id:
        return json.dumps({"type": "rejection", "message": "It's not your turn"})
    
    # The only action possible is do_skip when you are skipped
    if data["action"] != "do_skip" and len(player.skip_cards) > 0:
        data["action"] = "do_skip"
    
    if not is_sorting:
        if (not (data["action"] == "draw_deck" or data["action"] == "draw_discard")) and not player.drew_card:
            return json.dumps({"type": "rejection", "message": "YOU HAVE TO DRAW FIRST!!!!"})
    
    match data["action"]:
        case "draw_deck":
            # You can only draw once per turn
            if player.drew_card:
                return json.dumps({"type": "rejection", "message": "You already drew for this round!"})
            hand.append(game.deck.pop())
            player.drew_card = True
            player.save()
            game.save()
            conn.commit()
        
        case "draw_discard":
            # You can only draw once per turn
            if player.drew_card:
                return json.dumps({"type": "rejection", "message": "You already drew for this round!"})
            if len(game.discard) == 0:
                return json.dumps({"type": "rejection", "message": "Can't take from an empty discard pile!"})
            if game.discard[-1].rank is Rank.SKIP:
                return json.dumps({"type": "rejection", "message": "Can't take SKIP cards from the discard pile!"})
            hand.append(game.discard.pop())
            player.drew_card = True
            player.save()
            game.save()
            conn.commit()
        case "do_skip":
            pass
        
        case "put_down":
            if not player.completed_phase:
                return json.dumps(
                    {"type": "rejection", "message": "You need to complete your phase before you put down"})
            
            gamePhaseDeck = GamePhaseDeck.get_by_id(data["phase_deck_id"])
            cards = CardCollection([Card.fromJSONDict(x) for x in data["cards"]])
            
            if data["direction"] == "start":
                deckToTest = CardCollection(cards + gamePhaseDeck.deck)
            elif data["direction"] == "end":
                deckToTest = CardCollection(gamePhaseDeck.deck + cards)
            else:
                return json.dumps({"type": "rejection", "message": f"{data['direction']} is not a valid direction"})
            
            phase = gamePhaseDeck.phase
            
            rr = RE(phase)
            
            if rr.isFullyAccepted(deckToTest):
                # Remove the cards from the player's hand
                for card in cards:
                    if card not in hand:
                        return json.dumps({"type": "rejection", "message": f"{str(card)} is not in your hand"})
                    else:
                        hand.remove(card)
                player.save()
                
                gamePhaseDeck.deck = deckToTest
                gamePhaseDeck.save()
                conn.commit()
            else:
                return json.dumps({"type": "rejection", "message": "Unable to put down these cards to the phase!"})
        
        case "complete_phase":
            if player.completed_phase:
                return json.dumps({"type": "rejection", "message": "You've already completed your phase!"})
            
            cards = CardCollection(Card.fromJSONDict(x) for x in data["cards"])
            phase = game.phase_list[player.phase_index]
            rr = RE(phase)
            if rr.isFullyAccepted(cards):
                
                for phase_comp in phase.split('+'):
                    
                    num_cards = int(phase_comp[1:])
                    
                    card_component = CardCollection(cards[:num_cards])
                    # Make sure these cards are in the player's hand
                    for card in card_component:
                        if card not in hand:
                            return json.dumps(
                                {"type": "rejection", "message": f"This card {card} is not in your hand!"})
                    
                    # Remove the cards from the player's hand
                    for card in card_component:
                        hand.remove(card)
                    player.completed_phase = True
                    cards = CardCollection(cards[num_cards:])
                    # Create a new gamePhaseDeck
                    gamePhaseDeck = GamePhaseDeck(game_id=player.game_id, phase=phase_comp[:1], deck=card_component)
                    gamePhaseDeck.save()
                    
                    player.save()
                    conn.commit()
            
            else:
                return json.dumps({"type": "rejection", "message": "Not a valid phase!"})
        
        case "skip_player":
            if not player.drew_card:
                return json.dumps({"type": "rejection", "message": "Draw a card before you attempt to skip someone"})
            contains_skip = False
            skip_card = None
            for card in hand:
                if card.rank is Rank.SKIP:
                    contains_skip = True
                    skip_card = card
                    break
            if contains_skip:
                # Give the other player a skip card
                to_id = data["to"]
                to_player = Player.get_by_game_id_user_id(game_id, to_id)
                to_player.skip_cards.append(skip_card)
                hand.remove(skip_card)
                
                player.save()
                to_player.save()
                conn.commit()
                complete_turn = True
            
            else:
                return json.dumps({"type": "rejection", "message": "You don't have a skip card!"})
        
        case "discard":
            card_id = data["card_id"]
            selected_card = None
            for card in hand:
                if card.id == card_id:
                    selected_card = card
                    break
            if selected_card is not None:
                hand.remove(selected_card)
                game.discard.append(selected_card)
                
                player.save()
                game.save()
                conn.commit()
            complete_turn = True
        
        case "finish_hand":
            pass
        case "sort_by_color":
            pass
        case "sort_by_rank":
            pass
        case _:
            raise Exception(f"Unrecognized player option {data['action']}")
    
    # User had discarded, skipped, or been skipped
    # We need to advance the game to the next player
    if complete_turn:
        roomPlayers = [player for player in Player.all() if player.game_id == game.id]
        roomPlayers.sort(key=lambda p: p.turn_index)
        current_player_index = -1
        for i, roomPlayer in enumerate(roomPlayers):
            if roomPlayer.user_id == game.current_player:
                current_player_index = i
                break
        if i == -1:
            raise Exception(f"Couldn't find the current player!")
        
        current_player_index = (current_player_index + 1) % len(roomPlayers)
        next_player = roomPlayers[current_player_index]
        
        # Perform the skipping operations
        while len(next_player.skip_cards) > 0:
            next_player.drew_card = False
            game.discard.append(next_player.skip_cards.pop())
            player.save()
            next_player.save()
            conn.commit()
            current_player_index = (current_player_index + 1) % len(roomPlayers)
            next_player = roomPlayers[current_player_index]
        
        game.current_player = next_player.user_id
        player.drew_card = False
        
        player.save()
        game.save()
        conn.commit()
    
    # Player has completed their hand
    if len(player.hand) == 0:
        game.deck = Card.getNewDeck()
        random.shuffle(game.deck)
        game.discard = [game.deck.pop()]
        
        roomPlayers = [p for p in Player.all() if p.game_id == game_id]
        roomPlayers.sort(key=lambda p: p.turn_index)
        
        # Player has won
        if player.phase_index >= len(game.phase_list) - 1 and player.completed_phase:
            game.winner = player.user_id
        else:
            # Update the player info
            for i, roomPlayer in enumerate(roomPlayers):
                roomPlayer.hand = CardCollection([game.deck.pop() for _ in range(INITIAL_HAND_SIZE)])
                roomPlayer.drew_card = False
                # We move the player list up one turn
                roomPlayer.turn_index = (i + 1) % len(roomPlayers)
                if roomPlayer.completed_phase:
                    roomPlayer.phase_index = min(roomPlayer.phase_index + 1, len(game.phase_list) - 1)
                    roomPlayer.completed_phase = False
                    roomPlayer.skip_cards = CardCollection()
                
                roomPlayer.save()
        
        game.current_player = roomPlayers[-1].user_id
        # Remove all phase decks
        for gpd in GamePhaseDeck.all_where_game_id(game.id):
            gpd.delete()
        game.save()
        conn.commit()
    
    player_dict = player.to_json_dict()
    player_dict["phase"] = game.phase_list[player.phase_index]
    return json.dumps({"type": "get_player", "game_id": str(game_id), "user_id": str(user_id), "player": player_dict})


def handle_data(data, websocket):
    print()
    print(data)
    
    match data["type"]:
        case "connection":
            return json.dumps({"type": "connection"})
        case "disconnection":
            connected.remove(websocket)
        case "new_user":
            will_send = True
            if will_send:
                try:
                    # Add this new user to our databases
                    u = User(
                        id=uuid.uuid4(),
                        name=data["name"],
                    )
                    u.save()
                    conn.commit()
                    return json.dumps({"type": "new_user", "user": u.to_json_dict()})
                
                except Exception as e:
                    # This happens because the SQL statement failed
                    print(e)
                    conn.rollback()
                    return json.dumps(
                        {
                            "type": "rejection",
                            "message": f"User already exists with the name {data['name']}",
                        }
                    )
            else:
                return json.dumps(
                    {
                        "type": "rejection",
                        "message": f"User already exists with the name {data['name']}",
                    }
                )
        
        case "get_users":
            return json.dumps({"type": "ignore"})
        case "get_player":
            game_id = data["game_id"]
            user_id = data["user_id"]
            
            if not Game.exists(game_id):
                return json.dumps({"type": "ignore", "message": f"Game room {game_id} is not valid!"})
            
            game = Game.get_by_id(game_id)
            if Player.exists_by_game_id_user_id(game_id, user_id):
                player = Player.get_by_game_id_user_id(game_id, user_id)
                socket_to_player_id[websocket] = player.id
                player_dict = player.to_json_dict()
                if player.phase_index < len(game.phase_list):
                    player_dict["phase"] = game.phase_list[player.phase_index]
                else:
                    player_dict["phase"] = "WINNER"
                
                return json.dumps(
                    {
                        "type": "get_player",
                        "game_id": game_id,
                        "user_id": user_id,
                        "player": player_dict,
                    }
                )
            else:
                return json.dumps(
                    {
                        "type": "get_player",
                        "game_id": game_id,
                        "user_id": user_id,
                    }
                )
        
        case "create_game":
            return create_game(data)
        
        case "join_game":
            game_id = data["game_id"]
            user_id = data["user_id"]
            game = Game.get_by_id(game_id)
            
            if Player.exists_by_game_id_user_id(game_id, user_id):
                return json.dumps(
                    {
                        "type": "rejection",
                        "message": "You are already in that game!",
                    }
                )
            elif game.in_progress:
                return json.dumps(
                    {
                        "type": "rejection",
                        "message": "You can't join a game that's already in progress",
                    }
                )
            else:
                try:
                    p = Player(game_id=game_id, user_id=user_id)
                    p.save()
                    conn.commit()
                    
                    return json.dumps({"type": "ignore"})
                except Exception as e:
                    print(e)
                    user = User.get_by_id(user_id)
                    return json.dumps({"type": "rejection", "message": f"({user.name} cannot join game {game_id}"})
        case "unjoin_game":
            game_id = data["game_id"]
            user_id = data["user_id"]
            game = Game.get_by_id(game_id)
            
            if not Player.exists_by_game_id_user_id(game_id, user_id):
                return json.dumps(
                    {"type": "error", "message": f"Player with {user_id=} and {game_id=} does not exist!"})
            
            # The host is deleting the game
            if str(game.host) == user_id:
                game.delete()
                conn.commit()
            
            else:
                if game.in_progress:
                    return json.dumps({"type": "error", "message": "Cannot leave game after it has already started!"})
                Player.get_by_game_id_user_id(game_id, user_id).delete()
                conn.commit()
            
            return json.dumps({"type": "ignore"})
        case "get_games":
            return json.dumps({"type": "ignore"})
        case "edit_game_phase":
            game_id = data["game_id"]
            user_id = data["user_id"]
            
            new_phase = data["new_phase"]
            
            if len(new_phase) == 0:
                return json.dumps({"type": "rejection", "message": "Cannot submit an empty phase list!"})
            
            if not Game.exists(game_id):
                return json.dumps({"type": "rejection", "message": f"{game_id} is not a valid game id!"})
            
            game = Game.get_by_id(game_id)
            
            if game.in_progress:
                return json.dumps({"type": "rejection", "message": f"{game_id} is already in progress!"})
            
            if str(game.host) != user_id:
                return json.dumps({"type": "rejection",
                                   "message": "You are not the host of the game and cannot edit its phase!"})
            
            # Make sure every phase is valid
            try:
                for phase in new_phase:
                    RE(phase)
            except Exception as e:
                return json.dumps({"type": "rejection",
                                   "message": f"Invalid phase list {new_phase}! {e}"})
            
            game.phase_list = new_phase
            game.save()
            conn.commit()
            
            return json.dumps({"type": "ignore"})
        
        case "start_game":
            game_id = data["game_id"]
            user_id = data["user_id"]
            
            game = Game.get_by_id(game_id)
            
            if str(game.host) == user_id and not game.in_progress:
                player_list = [player for player in Player.all() if player.game_id == game.id]
                
                deck = Card.getNewDeck()
                random.shuffle(deck)
                random.shuffle(player_list)
                for i, player in enumerate(player_list):
                    player.phase_index = 0
                    player.turn_index = i
                    player.hand = CardCollection(deck.pop() for _ in range(INITIAL_HAND_SIZE))
                    # We need to delete the player first because otherwise, we can't reset the turn index
                    player.delete()
                    player.save()
                    conn.commit()
                
                game.discard = CardCollection()
                game.discard.append(deck.pop())
                game.deck = CardCollection(deck)
                game.in_progress = True
                game.current_player = player_list[0].user_id
                game.save()
                conn.commit()
                return json.dumps({"type": "ignore"})
            else:
                return json.dumps(
                    {
                        "type": "rejection",
                        "message": "You are not the host and cannot start this game",
                    }
                )
        case "player_action":
            return player_action(data)
        case _:
            return json.dumps(
                {
                    "type": "rejection",
                    "message": f"Unrecognized type {data['type']}",
                }
            )


async def handler(websocket):
    connected.add(websocket)
    
    async for event in websocket:
        data = json.loads(event)
        message = handle_data(data, websocket)
        print(message)
        await websocket.send(message)
        await send_games()
        await send_users()
        await send_players()
    if websocket in connected:
        connected.remove(websocket)
    if websocket in socket_to_player_id:
        socket_to_player_id.pop(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    
    if DEBUG:
        # Create our users
        if not User.exists_by_name("Alfredo"):
            handle_data({"type": "new_user", "name": "Alfredo"}, None)
        if not User.exists_by_name("Naly"):
            handle_data({"type": "new_user", "name": "Naly"}, None)
        if not User.exists_by_name("Yer"):
            handle_data({"type": "new_user", "name": "Yer"}, None)
        if not User.exists_by_name("Averie"):
            handle_data({"type": "new_user", "name": "Averie"}, None)
        
        alfredo = User.get_by_name("Alfredo")
        naly = User.get_by_name("Naly")
        yer = User.get_by_name("Yer")
        averie = User.get_by_name("Averie")
        
        # Create a game
        handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
        game0 = Game.all()[0]
        
        # Have a player join and unjoin
        handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
        handle_data({"type": "unjoin_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
        
        # Have a host delete an empty game room
        handle_data({"type": "unjoin_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
        
        # Have a host delete a game that's started
        handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
        game0 = Game.all()[0]
        handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
        handle_data({"type": "start_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
        handle_data({"type": "unjoin_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
        
        # Create the game rooms for web-browser testing
        handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
        game0 = Game.all()[0]
        handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
        handle_data({"type": "create_game", "user_id": str(yer.id)}, None)
        game1 = Game.all()[0] if Game.all()[0].id != game0.id else Game.all()[1]
        
        handle_data({"type": "start_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
        handle_data({"type": "join_game", "user_id": str(alfredo.id), "game_id": str(game1.id)}, None)
        handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game1.id)}, None)
        handle_data({"type": "join_game", "user_id": str(averie.id), "game_id": str(game1.id)}, None)
        handle_data({"type": "start_game", "user_id": str(yer.id), "game_id": str(game1.id)}, None)
        game0 = Game.get_by_id(game0.id)
        game1 = Game.get_by_id(game1.id)
        
        alfredo_p = Player.get_by_game_id_user_id(game0.id, alfredo.id)
        naly_p = Player.get_by_game_id_user_id(game0.id, naly.id)
    
    asyncio.run(main())

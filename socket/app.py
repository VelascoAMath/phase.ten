import asyncio
import datetime
import json
import random
from configparser import ConfigParser

import peewee
import websockets

from Card import Card, Rank
from CardCollection import CardCollection
from GameMessage import GameMessage
from Gamephasedecks import Gamephasedecks
from Games import Games
from Players import Players
from RE import RE
from Users import Users

DEBUG = False

connected = set()
socket_to_player_id = {}
next_player_list = []

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

# Create databases

parser = ConfigParser()
config = {}

parser.read("database.ini")
if parser.has_section("postgresql"):
	for param in parser.items("postgresql"):
		config[param[0]] = param[1]
else:
	raise Exception(f"No postgresql section in database.ini!")

db = peewee.PostgresqlDatabase(**config)
db.execute_sql(
	"""
do $$ BEGIN
	create type game_type as enum ('NORMAL', 'LEGACY', 'ADVANCEMENT');
exception
	when duplicate_object then null;
end $$;
"""
)
db.execute_sql(
	"""
create sequence if not exists players_turn_index_seq AS integer;
create sequence if not exists game_message_index_seq AS integer;
"""
)

if DEBUG:
	db.drop_tables([Users, Games, Players, Gamephasedecks, GameMessage])

# create_databases()
db.create_tables([Users, Games, Players, Gamephasedecks, GameMessage])

# Create the bots
for name in set(f"Bot{i + 1}" for i in range(6)) - set(
	u.name for u in Users.select().where(Users.is_bot)
):
	Users(name=name, display=name, is_bot=True).save(force_insert=True)


async def send_users():
	user_list: list[Users] = list(Users.select())
	websockets.broadcast(
		connected,
		json.dumps(
			{"type": "get_users", "users": [u.to_json_dict() for u in user_list]}
		),
	)


async def send_players():
	socket_to_delete = set()
	for socket, player_id in socket_to_player_id.items():
		# This player is deleted
		# We'll need to send a different player to this socket
		
		if not Players.exists(player_id):
			socket_to_delete.add(socket)
			break
		
		player: Players = Players.get_by_id(player_id)
		game = player.game
		user_id = player.user.id
		game_id = game.id
		player_dict = player.to_json_dict()
		if player.phase_index < len(game.phase_list):
			player_dict["phase"] = game.phase_list[player.phase_index]
		else:
			player_dict["phase"] = "WINNER"
		
		await socket.send(
			json.dumps(
				{
					"type": "get_player",
					"game_id": str(game_id),
					"user_id": str(user_id),
					"player": player_dict,
				}
			)
		)
		game_dict = game.to_json_dict()
		
		# Don't send the entire deck
		if "deck" in game_dict:
			del game_dict["deck"]
		
		game_dict["players"] = []
		game_dict["users"] = []
		
		player_list = list(
			Players.select().where(Players.game == game).order_by(Players.turn_index)
		)
		for player in player_list:
			user_dict = player.user.to_json_dict()
			player_dict = player.to_json_dict()
			player_dict["name"] = player.user.name
			player_dict["display"] = player.user.display
			player_dict["hand_size"] = len(player.hand)
			
			if "hand" in player_dict:
				del player_dict["hand"]
			
			if "token" in user_dict:
				del user_dict["token"]
			
			game_dict["players"].append(player_dict)
			game_dict["users"].append(user_dict)
		
		game_dict["phase_decks"] = [
			x.to_json_dict()
			for x in Gamephasedecks.select().where(Gamephasedecks.game == game)
		]
		
		game_dict["message_list"] = [
			{"message": gm.message, "index": gm.index}
			for gm in GameMessage.select()
			.where(GameMessage.game == game)
			.order_by(-GameMessage.index)
		]
		
		await socket.send(json.dumps({"type": "get_game", "game": game_dict}))


async def send_games():
	game_list = []
	for game in Games.select():
		game_dict = game.to_json_dict()
		if "deck" in game_dict:
			del game_dict["deck"]
		if "discard" in game_dict:
			del game_dict["discard"]
		
		game_dict["users"] = []
		
		user_list = Users.select().join(Players).join(Games).where(Games.id == game.id)
		
		for user in user_list:
			user_dict = user.to_json_dict()
			if "token" in user_dict:
				del user_dict["token"]
			game_dict["users"].append(user_dict)
		
		game_list.append(game_dict)
	
	websockets.broadcast(
		connected, json.dumps({"type": "get_games", "games": game_list})
	)


def create_game(data):
	user_id = data["user_id"]
	if not Users.exists(user_id):
		return json.dumps(
			{
				"type": "rejection",
				"message": f"User ID {user_id} is not valid!",
			}
		)
	else:
		try:
			u = Users.get_by_id(user_id)
			g = Games(
				phase_list=DEFAULT_PHASE_LIST,
				deck=CardCollection(),
				discard=CardCollection(),
				host=u,
				current_player=u,
				in_progress=False,
			)
			g.save(force_insert=True)
			
			p = Players(game=g, user=u)
			p.save(force_insert=True)
			# For each game, let's also list the players who are in it
			game_dict = g.to_json_dict()
			game_dict["users"] = [u.to_json_dict()]
			
			return json.dumps({"type": "create_game", "game": game_dict})
		
		except Exception:
			return json.dumps({"type": "rejection", "message": "Cannot create game"})


def player_action(data):
	player_id = data["player_id"]
	
	player: Players = Players.get_by_id(player_id)
	
	hand = player.hand
	game = player.game
	
	complete_turn = False
	
	# Players are always allowed to sort their cards
	# Any other action requires you to wait until your turn
	is_sorting = False
	if data["action"] == "sort_by_color":
		hand.sort(key=lambda x: x.color.value)
		player.save()
		is_sorting = True
	elif data["action"] == "sort_by_rank":
		hand.sort(key=lambda x: x.rank.value)
		player.save()
		is_sorting = True
	elif game.current_player != player.user:
		return json.dumps({"type": "rejection", "message": "It's not your turn"})
	
	# The only action possible is do_skip when you are skipped
	if data["action"] != "do_skip" and len(player.skip_cards) > 0:
		data["action"] = "do_skip"
	
	if not is_sorting:
		if (
			not (data["action"] == "draw_deck" or data["action"] == "draw_discard")
		) and not player.drew_card:
			return json.dumps(
				{"type": "rejection", "message": "YOU HAVE TO DRAW FIRST!!!!"}
			)
	
	match data["action"]:
		case "draw_deck":
			# You can only draw once per turn
			if player.drew_card:
				return json.dumps(
					{"type": "rejection", "message": "You already drew for this round!"}
				)
			hand.append(game.deck.pop())
			player.drew_card = True
			
			if len(game.deck) == 0:
				random.shuffle(game.discard)
				game.deck.extend(game.discard)
				game.discard = CardCollection()
			
			player.save()
			game.save()
		
		case "draw_discard":
			# You can only draw once per turn
			if player.drew_card:
				return json.dumps(
					{"type": "rejection", "message": "You already drew for this round!"}
				)
			if len(game.discard) == 0:
				return json.dumps(
					{
						"type": "rejection",
						"message": "Can't take from an empty discard pile!",
					}
				)
			if game.discard[-1].rank is Rank.SKIP:
				return json.dumps(
					{
						"type": "rejection",
						"message": "Can't take SKIP cards from the discard pile!",
					}
				)
			hand.append(game.discard.pop())
			player.drew_card = True
			player.save()
			game.save()
		case "do_skip":
			pass
		
		case "put_down":
			if not player.completed_phase:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You need to complete your phase before you put down",
					}
				)
			
			gamePhaseDeck: Gamephasedecks = Gamephasedecks.get_by_id(
				data["phase_deck_id"]
			)
			cards = CardCollection([Card.fromJSONDict(x) for x in data["cards"]])
			
			if data["direction"] == "start":
				deckToTest = CardCollection(cards + gamePhaseDeck.deck)
			elif data["direction"] == "end":
				deckToTest = CardCollection(gamePhaseDeck.deck + cards)
			else:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{data['direction']} is not a valid direction",
					}
				)
			
			phase = gamePhaseDeck.phase
			
			rr = RE(phase)
			
			if rr.isFullyAccepted(deckToTest):
				# Remove the cards from the player's hand
				for card in cards:
					if card not in hand:
						return json.dumps(
							{
								"type": "rejection",
								"message": f"{str(card)} is not in your hand",
							}
						)
					else:
						hand.remove(card)
				player.save()
				
				gamePhaseDeck.deck = deckToTest
				gamePhaseDeck.save()
			else:
				return json.dumps(
					{
						"type": "rejection",
						"message": "Unable to put down these cards to the phase!",
					}
				)
		
		case "complete_phase":
			if player.completed_phase:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You've already completed your phase!",
					}
				)
			
			cards = CardCollection(Card.fromJSONDict(x) for x in data["cards"])
			phase = game.phase_list[player.phase_index]
			rr = RE(phase)
			if rr.isFullyAccepted(cards):
				for phase_comp in phase.split("+"):
					num_cards = int(phase_comp[1:])
					
					card_component = CardCollection(cards[:num_cards])
					# Make sure these cards are in the player's hand
					for card in card_component:
						if card not in hand:
							return json.dumps(
								{
									"type": "rejection",
									"message": f"This card {card} is not in your hand!",
								}
							)
					
					# Remove the cards from the player's hand
					for card in card_component:
						hand.remove(card)
					player.completed_phase = True
					cards = CardCollection(cards[num_cards:])
					# Create a new gamePhaseDeck
					gamePhaseDeck = Gamephasedecks(
						game=Games.get_by_id(player.game),
						phase=phase_comp[:1],
						deck=card_component,
					)
					gamePhaseDeck.save(force_insert=True)
					
					player.save()
			
			else:
				return json.dumps(
					{"type": "rejection", "message": "Not a valid phase!"}
				)
		
		case "skip_player":
			if not player.drew_card:
				return json.dumps(
					{
						"type": "rejection",
						"message": "Draw a card before you attempt to skip someone",
					}
				)
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
				to_user = Users.get_by_id(to_id)
				to_player: Players = Players.get(game=game, user=to_user)
				to_player.skip_cards.append(skip_card)
				hand.remove(skip_card)
				
				game.last_move_made = datetime.datetime.now(datetime.timezone.utc)
				game.save()
				player.save()
				to_player.save()
				
				game_message = GameMessage(
					game=game,
					message=f"{player.user.name} has skipped {to_player.user.name}",
				)
				game_message.save(force_insert=True)
				
				complete_turn = True
			
			else:
				return json.dumps(
					{"type": "rejection", "message": "You don't have a skip card!"}
				)
		
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
				game.last_move_made = datetime.datetime.now(datetime.timezone.utc)
				
				player.save()
				game.save()
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
		roomPlayers: list[Players] = list(
			Players.select().where(Players.game == game).order_by(Players.turn_index)
		)
		current_player_index = -1
		for i, roomPlayer in enumerate(roomPlayers):
			if roomPlayer.user == game.current_player:
				current_player_index = i
				break
		if current_player_index == -1:
			raise Exception(f"Couldn't find the current player!")
		
		current_player_index = (current_player_index + 1) % len(roomPlayers)
		next_player = roomPlayers[current_player_index]
		
		# Perform the skipping operations
		while len(next_player.skip_cards) > 0:
			next_player.drew_card = False
			game.discard.append(next_player.skip_cards.pop())
			player.save()
			next_player.save()
			current_player_index = (current_player_index + 1) % len(roomPlayers)
			next_player = roomPlayers[current_player_index]
		
		game.current_player = next_player.user
		
		next_player_list.append(next_player)
		player.drew_card = False
		
		player.save()
		game.save()
	
	# Player has completed their hand
	if len(player.hand) == 0:
		game.deck = CardCollection.getNewDeck()
		random.shuffle(game.deck)
		game.discard = CardCollection([game.deck.pop()])
		
		roomPlayers = list(
			Players.select().where(Players.game == game).order_by(Players.turn_index)
		)
		
		# Player has won
		if player.phase_index >= len(game.phase_list) - 1 and player.completed_phase:
			game.winner = player.user
		else:
			game_message = GameMessage(
				game=game, message=f"{player.user.name} has won the round!"
			)
			game_message.save(force_insert=True)
			# Update the player info
			for i, roomPlayer in enumerate(roomPlayers):
				roomPlayer.hand = CardCollection(
					[game.deck.pop() for _ in range(INITIAL_HAND_SIZE)]
				)
				roomPlayer.skip_cards = CardCollection()
				roomPlayer.drew_card = False
				# We move the player list up one turn
				if roomPlayer.turn_index >= len(roomPlayers):
					roomPlayer.turn_index = (roomPlayer.turn_index + 1) % len(
						roomPlayers
					)
				else:
					roomPlayer.turn_index = (
						                        (roomPlayer.turn_index + 1) % len(roomPlayers)
					                        ) + len(roomPlayers)
				if roomPlayer.completed_phase:
					roomPlayer.phase_index = min(
						roomPlayer.phase_index + 1, len(game.phase_list) - 1
					)
					roomPlayer.completed_phase = False
				
				roomPlayer.save()
		
		game.current_player = roomPlayers[-1].user
		if next_player_list:
			next_player_list.pop()
		next_player_list.append(roomPlayers[-1])
		
		# Remove all phase decks
		for gpd in (
			Gamephasedecks.select()
				.where(Gamephasedecks.game == game)
				.order_by(Gamephasedecks.id)
		):
			gpd.delete_instance()
		game.save()
	
	player_dict = player.to_json_dict()
	player_dict["phase"] = game.phase_list[player.phase_index]
	return json.dumps(
		{
			"type": "get_player",
			"game_id": str(game.id),
			"user_id": str(player.user.id),
			"player": player_dict,
		}
	)


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
					u = Users(
						name=data["name"],
						display=data["name"],
					)
					u.save(force_insert=True)
					return json.dumps({"type": "new_user", "user": u.to_json_dict()})
				
				except Exception as e:
					# This happens because the SQL statement failed
					print(e)
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
		case "edit_display_name":
			user_id = data["user_id"]
			new_display_name: str = data["display"]
			
			if Users.exists(user_id):
				if len(new_display_name) == 0:
					return json.dumps(
						{"type": "rejection", "message": f"Must have display name!"}
					)
				
				user: Users = Users.get_by_id(user_id)
				user.display = new_display_name
				user.save()
				
				return json.dumps({"type": "new_user", "user": user.to_json_dict()})
			
			else:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{user_id} is not a valid user id!",
					}
				)
		
		case "get_users":
			return json.dumps({"type": "ignore"})
		case "get_player":
			game_id = data["game_id"]
			user_id = data["user_id"]
			
			if not Games.exists(game_id):
				return json.dumps(
					{"type": "ignore", "message": f"Game room {game_id} is not valid!"}
				)
			
			game = Games.get_by_id(game_id)
			user = Users.get_by_id(user_id)
			player = Players.get_or_none(game=game, user=user)
			
			if player is None:
				return json.dumps(
					{
						"type": "get_player",
						"game_id": game_id,
						"user_id": user_id,
					}
				)
			
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
		
		case "create_game":
			return create_game(data)
		
		case "join_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			game = Games.get_by_id(game_id)
			user = Users.get_by_id(user_id)
			
			p = Players.get_or_none(game=game, user=user)
			
			if p is not None:
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
					p = Players(game=game, user=user)
					p.save(force_insert=True)
					
					return json.dumps({"type": "ignore"})
				except Exception as e:
					print(e)
					user = Users.get_by_id(user_id)
					return json.dumps(
						{
							"type": "rejection",
							"message": f"({user.name} cannot join game {game_id}",
						}
					)
		case "add_bot":
			game_id = data["game_id"]
			user_id = data["user_id"]
			
			if not Games.exists(game_id):
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{game_id} is not a valid game id!",
					}
				)
			
			game: Games = Games.get_by_id(game_id)
			
			if game.in_progress:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{game_id} is already in progress!",
					}
				)
			
			if str(game.host.id) != user_id:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You are not the host of the game and cannot edit its phase!",
					}
				)
			
			bots: list[Users] = list(
				Users.select()
				.where(
					Users.is_bot
					& (
						Users.id.not_in(
							Players.select(Players.user).where(Players.game == game)
						)
					)
				)
				.order_by(Users.name)
			)
			
			if bots:
				bot = Players(game=game, user=bots[0])
				bot.save(force_insert=True)
				return json.dumps({"type": "ignore"})
			else:
				return json.dumps(
					{"type": "rejection", "message": f"Game is already full of bots!"}
				)
		
		case "remove_bot":
			game_id = data["game_id"]
			user_id = data["user_id"]
			
			if not Games.exists(game_id):
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{game_id} is not a valid game id!",
					}
				)
			
			game: Games = Games.get_by_id(game_id)
			
			if game.in_progress:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{game_id} is already in progress!",
					}
				)
			
			if str(game.host.id) != user_id:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You are not the host of the game and cannot edit its phase!",
					}
				)
			
			bots: list[Users] = list(
				Users.select()
				.where(
					Users.is_bot
					& (
						Users.id.in_(
							Players.select(Players.user)
							.where(Players.game == game)
							.order_by(Players.id)
						)
					)
				)
				.order_by(Users.name)
			)
			
			if bots:
				bot: Players = Players.get(
					(Players.game == game) & (Players.user == bots[-1])
				)
				bot.delete_instance()
				return json.dumps({"type": "ignore"})
			else:
				return json.dumps(
					{"type": "rejection", "message": f"Game has no bots!"}
				)
		
		case "unjoin_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			game = Games.get_by_id(game_id)
			user = Users.get_by_id(user_id)
			player = Players.get_or_none(game=game, user=user)
			
			if player is None:
				return json.dumps(
					{
						"type": "error",
						"message": f"Player with {user_id=} and {game_id=} does not exist!",
					}
				)
			
			# The host is deleting the game
			if game.host == user:
				Gamephasedecks.delete().where(Gamephasedecks.game == game).execute()
				game.delete_instance()
				player.delete_instance()
			else:
				if game.in_progress:
					return json.dumps(
						{
							"type": "error",
							"message": "Cannot leave game after it has already started!",
						}
					)
				player.delete_instance()
			
			return json.dumps({"type": "ignore"})
		
		case "get_games":
			return json.dumps({"type": "ignore"})
		case "edit_player_time_limit":
			print(data)
			
			user_id = data["user_id"]
			game_id = data["game_id"]
			
			if not Users.exists(user_id):
				return json.dumps(
					{
						"type": "rejection",
						"messsage": f"{user_id} is an invalid user id!",
					}
				)
			
			if not Games.exists(game_id):
				return json.dumps(
					{
						"type": "rejection",
						"messsage": f"{game_id} is an invalid game id!",
					}
				)
			
			user = Users.get_by_id(user_id)
			game = Games.get_by_id(game_id)
			
			if game.host != user:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You are not the host of the game!",
					}
				)
			
			game.player_time_limit = datetime.timedelta(
				days=data["days"],
				seconds=data["hours"] * 3600 + data["minutes"] * 60 + data["seconds"],
			)
			game.save()
			
			print(game.player_time_limit)
			
			return json.dumps({"type": "ignore"})
		
		case "edit_game_phase":
			game_id = data["game_id"]
			user_id = data["user_id"]
			
			new_phase = data["new_phase"]
			
			if len(new_phase) == 0:
				return json.dumps(
					{
						"type": "rejection",
						"message": "Cannot submit an empty phase list!",
					}
				)
			
			if not Games.exists(game_id):
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{game_id} is not a valid game id!",
					}
				)
			
			game = Games.get_by_id(game_id)
			
			if game.in_progress:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"{game_id} is already in progress!",
					}
				)
			
			if str(game.host.id) != user_id:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You are not the host of the game and cannot edit its phase!",
					}
				)
			
			# Make sure every phase is valid
			try:
				for phase in new_phase:
					RE(phase)
			except Exception as e:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"Invalid phase list {new_phase}! {e}",
					}
				)
			
			game.phase_list = new_phase
			game.save()
			
			return json.dumps({"type": "ignore"})
		
		case "start_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			
			game = Games.get_by_id(game_id)
			
			if str(game.host.id) == user_id and not game.in_progress:
				player_list: list[Players] = list(Players.select().where(Players.game == game))
				
				deck = CardCollection.getNewDeck()
				random.shuffle(deck)
				random.shuffle(player_list)
				
				for i, player in enumerate(player_list):
					player.phase_index = 0
					player.turn_index = i
					player.hand = CardCollection(
						deck.pop() for _ in range(INITIAL_HAND_SIZE)
					)
					# We need to delete the player first because otherwise, we can't reset the turn index
					player.delete_instance()
					player.save(force_insert=True)
				
				game.discard = CardCollection()
				game.discard.append(deck.pop())
				game.deck = CardCollection(deck)
				game.in_progress = True
				game.current_player = player_list[0].user
				game.last_move_made = datetime.datetime.now(datetime.timezone.utc)
				game.save()
				return json.dumps({"type": "ignore"})
			else:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You are not the host and cannot start this game",
					}
				)
		case "skip_slow_player":
			player_id = data["player_id"]
			
			if Players.exists(player_id):
				player: Players = Players.get_by_id(player_id)
				game = player.game
				
				if (
					game.last_move_made + game.player_time_limit
				) < datetime.datetime.now(datetime.timezone.utc):
					roomPlayers: list[Players] = list(
						Players.select()
						.where(Players.game == game)
						.order_by(Players.turn_index)
					)
					
					next_player: Players = Players.get(
						(Players.user == game.current_player) & (Players.game == game)
					)
					next_player.save()
					i = (roomPlayers.index(next_player) + 1) % len(roomPlayers)
					next_player = roomPlayers[i]
					
					while next_player.skip_cards:
						next_player.skip_cards.pop()
						next_player.drew_card = False
						i = (i + 1) % len(roomPlayers)
						next_player = roomPlayers[i]
						next_player.save()
					
					game.current_player = next_player.user
					game.last_move_made = datetime.datetime.now(datetime.timezone.utc)
					game.save()
					
					return json.dumps({"type": "ignore"})
				else:
					return json.dumps(
						{
							"type": "rejection",
							"message": f"Can't skip {game.current_player.name} yet! They're not slow",
						}
					)
			
			else:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"Invalid player id {player_id}!",
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
	
	while True:
		try:
			async for event in websocket:
				data = json.loads(event)
				message = handle_data(data, websocket)
				print(message)
				await websocket.send(message)
				
				while next_player_list:
					next_player: Players = next_player_list.pop()
					if next_player.user.is_bot:
						while (
							next_player.user.is_bot
							and next_player.game.current_player == next_player.user
						):
							next_player.make_next_move()
							handle_data(next_player.make_next_move(), websocket)
							await send_games()
							await send_users()
							await send_players()
							next_player = Players.get_by_id(next_player.id)
					else:
						websockets.broadcast(
							connected,
							json.dumps(
								{
									"type": "next_player",
									"user_id": str(next_player.user.id),
								}
							),
						)
				
				# Look for any bots which are ready to play and make them perform their next moves
				# We have extra checks to make the sure the game has started and has no winner
				bot_players_ready_to_go = [
					p
					for p in Players.select()
					if (
						p.user.is_bot
						and p.game.current_player == p.user
						and p.game.in_progress
						and p.game.winner is None
					)
				]
				
				for next_player in bot_players_ready_to_go:
					next_move = next_player.make_next_move()
					handle_data(next_move, websocket)
					await send_games()
					await send_users()
					await send_players()
				
				await send_games()
				await send_users()
				await send_players()
		except:
			pass
		
		if websocket in connected:
			connected.remove(websocket)
		if websocket in socket_to_player_id:
			socket_to_player_id.pop(websocket)


async def main():
	async with websockets.serve(handler, "", 8005):
		await asyncio.Future()  # run forever


if __name__ == "__main__":
	if DEBUG:
		# Create our users
		if Users.get_or_none(name="Alfredo") is None:
			handle_data({"type": "new_user", "name": "Alfredo"}, None)
		if Users.get_or_none(name="Naly") is None:
			handle_data({"type": "new_user", "name": "Naly"}, None)
		if Users.get_or_none(name="Yer") is None:
			handle_data({"type": "new_user", "name": "Yer"}, None)
		if Users.get_or_none(name="Averie") is None:
			handle_data({"type": "new_user", "name": "Averie"}, None)
		
		alfredo = Users.get(name="Alfredo")
		naly = Users.get(name="Naly")
		yer = Users.get(name="Yer")
		averie = Users.get(name="Averie")
		
		# Create a game
		handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
		game0 = Games.get()
		
		# Have a player join and unjoin
		handle_data(
			{"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)},
			None,
		)
		handle_data(
			{"type": "unjoin_game", "user_id": str(naly.id), "game_id": str(game0.id)},
			None,
		)
		
		# Have a host delete an empty game room
		handle_data(
			{
				"type": "unjoin_game",
				"user_id": str(alfredo.id),
				"game_id": str(game0.id),
			},
			None,
		)
		
		# Have a host delete a game that's started
		handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
		game0 = Games.get()
		handle_data(
			{"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)},
			None,
		)
		handle_data(
			{
				"type": "start_game",
				"user_id": str(alfredo.id),
				"game_id": str(game0.id),
			},
			None,
		)
		handle_data(
			{
				"type": "unjoin_game",
				"user_id": str(alfredo.id),
				"game_id": str(game0.id),
			},
			None,
		)
		
		# Create the game rooms for web-browser testing
		handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
		game0 = Games.get()
		handle_data(
			{"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)},
			None,
		)
		handle_data({"type": "create_game", "user_id": str(yer.id)}, None)
		game1 = Games.get(Games.id != game0.id)
		
		handle_data(
			{
				"type": "start_game",
				"user_id": str(alfredo.id),
				"game_id": str(game0.id),
			},
			None,
		)
		handle_data(
			{"type": "join_game", "user_id": str(alfredo.id), "game_id": str(game1.id)},
			None,
		)
		handle_data(
			{"type": "join_game", "user_id": str(naly.id), "game_id": str(game1.id)},
			None,
		)
		handle_data(
			{"type": "join_game", "user_id": str(averie.id), "game_id": str(game1.id)},
			None,
		)
		handle_data(
			{"type": "start_game", "user_id": str(yer.id), "game_id": str(game1.id)},
			None,
		)
		game0 = Games.get_by_id(game0.id)
		game1 = Games.get_by_id(game1.id)
		
		alfredo_p = Players.get(game=game0, user=alfredo)
		naly_p = Players.get(game=game0, user=naly)
	
	asyncio.run(main())

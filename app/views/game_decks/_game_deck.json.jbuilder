json.extract! game_deck, :id, :game_id, :card_id, :order, :created_at, :updated_at
json.url game_deck_url(game_deck, format: :json)

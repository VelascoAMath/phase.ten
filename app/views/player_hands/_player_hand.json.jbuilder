json.extract! player_hand, :id, :game_id, :player_id, :card_id, :order, :created_at, :updated_at
json.url player_hand_url(player_hand, format: :json)

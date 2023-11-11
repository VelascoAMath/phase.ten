json.extract! room, :id, :player_id, :game_id, :created_at, :updated_at
json.url room_url(room, format: :json)

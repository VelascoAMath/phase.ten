class Player < ApplicationRecord
    has_many :player_hands
    has_many :rooms, through: :rooms


end

class Player < ApplicationRecord
    has_many :player_hands
    has_many :rooms, through: :rooms

    has_secure_password


end

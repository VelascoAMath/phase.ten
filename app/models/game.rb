class Game < ApplicationRecord
    has_many :players, through: :rooms
end

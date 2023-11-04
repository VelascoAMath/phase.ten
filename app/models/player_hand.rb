class PlayerHand < ApplicationRecord
  belongs_to :game
  belongs_to :card
  
  has_many :players
end

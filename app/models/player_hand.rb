class PlayerHand < ApplicationRecord
  belongs_to :game
  belongs_to :card
  
  belongs_to :players
end

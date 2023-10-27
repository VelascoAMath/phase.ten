class PlayerHand < ApplicationRecord
  belongs_to :game
  belongs_to :player
  belongs_to :card
end

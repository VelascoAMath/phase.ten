class AddPlayerHandToPlayer < ActiveRecord::Migration[7.1]
  def change
    add_reference :players, :player_hand
  end
end

class CreatePlayerOrders < ActiveRecord::Migration[7.1]
  def change
    create_table :player_orders do |t|
      t.references :game, null: false, foreign_key: true
      t.references :player, null: false, foreign_key: true
      t.integer :order
      
      t.timestamps
    end
  end
end

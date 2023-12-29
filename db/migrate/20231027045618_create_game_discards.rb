class CreateGameDiscards < ActiveRecord::Migration[7.1]
  def change
    create_table :game_discards do |t|
      t.references :game, null: false, foreign_key: true
      t.references :card, null: false, foreign_key: true
      t.integer :order

      t.timestamps
    end
  end
end

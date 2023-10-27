class AddUniqueNameToPlayer < ActiveRecord::Migration[7.1]
  def change
    add_index :players, :name, unique: true
  end
end

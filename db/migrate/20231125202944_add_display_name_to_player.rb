class AddDisplayNameToPlayer < ActiveRecord::Migration[7.1]
  def change
    add_column :players, :display_name, :string, null: false
    rename_column :players, :name, :user_name
    change_column_null :players, :user_name, false
    add_index :players, :user_name, unique: true, if_not_exists: true
  end
end

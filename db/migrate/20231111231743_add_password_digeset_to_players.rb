class AddPasswordDigesetToPlayers < ActiveRecord::Migration[7.1]
  def change
    add_column :players, :password_digest, :string
  end
end

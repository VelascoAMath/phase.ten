class AddRankColorToCard < ActiveRecord::Migration[7.1]
  def change
    add_column :cards, :rank, :integer
    add_column :cards, :color, :integer
  end
end

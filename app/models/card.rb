class Card < ApplicationRecord
	enum :rank, [:one, :two, :three, :four, :five, :six, :seven, :eight, :nine, :ten, :eleven, :twelve, :skip, :wild], prefix: true
	enum :color, [:red, :blue, :green, :yellow, :skip, :wild], prefix: true
end

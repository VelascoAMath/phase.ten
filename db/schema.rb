# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.1].define(version: 2023_10_27_045618) do
  create_table "cards", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "rank"
    t.integer "color"
  end

  create_table "game_decks", force: :cascade do |t|
    t.integer "game_id", null: false
    t.integer "card_id", null: false
    t.integer "order"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["card_id"], name: "index_game_decks_on_card_id"
    t.index ["game_id"], name: "index_game_decks_on_game_id"
  end

  create_table "game_discards", force: :cascade do |t|
    t.integer "game_id", null: false
    t.integer "card_id", null: false
    t.integer "order"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["card_id"], name: "index_game_discards_on_card_id"
    t.index ["game_id"], name: "index_game_discards_on_game_id"
  end

  create_table "games", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "phase_decks", force: :cascade do |t|
    t.integer "game_id", null: false
    t.integer "player_id", null: false
    t.integer "card_id", null: false
    t.integer "order"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["card_id"], name: "index_phase_decks_on_card_id"
    t.index ["game_id"], name: "index_phase_decks_on_game_id"
    t.index ["player_id"], name: "index_phase_decks_on_player_id"
  end

  create_table "phase_orders", force: :cascade do |t|
    t.integer "game_id", null: false
    t.integer "player_id", null: false
    t.integer "order"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["game_id"], name: "index_phase_orders_on_game_id"
    t.index ["player_id"], name: "index_phase_orders_on_player_id"
  end

  create_table "player_hands", force: :cascade do |t|
    t.integer "game_id", null: false
    t.integer "player_id", null: false
    t.integer "card_id", null: false
    t.integer "order"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["card_id"], name: "index_player_hands_on_card_id"
    t.index ["game_id"], name: "index_player_hands_on_game_id"
    t.index ["player_id"], name: "index_player_hands_on_player_id"
  end

  create_table "player_orders", force: :cascade do |t|
    t.integer "game_id", null: false
    t.integer "player_id", null: false
    t.integer "order"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["game_id"], name: "index_player_orders_on_game_id"
    t.index ["player_id"], name: "index_player_orders_on_player_id"
  end

  create_table "players", force: :cascade do |t|
    t.string "name"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_players_on_name", unique: true
  end

  add_foreign_key "game_decks", "cards"
  add_foreign_key "game_decks", "games"
  add_foreign_key "game_discards", "cards"
  add_foreign_key "game_discards", "games"
  add_foreign_key "phase_decks", "cards"
  add_foreign_key "phase_decks", "games"
  add_foreign_key "phase_decks", "players"
  add_foreign_key "phase_orders", "games"
  add_foreign_key "phase_orders", "players"
  add_foreign_key "player_hands", "cards"
  add_foreign_key "player_hands", "games"
  add_foreign_key "player_hands", "players"
  add_foreign_key "player_orders", "games"
  add_foreign_key "player_orders", "players"
end

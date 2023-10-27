require "application_system_test_case"

class GameDecksTest < ApplicationSystemTestCase
  setup do
    @game_deck = game_decks(:one)
  end

  test "visiting the index" do
    visit game_decks_url
    assert_selector "h1", text: "Game decks"
  end

  test "should create game deck" do
    visit game_decks_url
    click_on "New game deck"

    fill_in "Card", with: @game_deck.card_id
    fill_in "Game", with: @game_deck.game_id
    fill_in "Order", with: @game_deck.order
    click_on "Create Game deck"

    assert_text "Game deck was successfully created"
    click_on "Back"
  end

  test "should update Game deck" do
    visit game_deck_url(@game_deck)
    click_on "Edit this game deck", match: :first

    fill_in "Card", with: @game_deck.card_id
    fill_in "Game", with: @game_deck.game_id
    fill_in "Order", with: @game_deck.order
    click_on "Update Game deck"

    assert_text "Game deck was successfully updated"
    click_on "Back"
  end

  test "should destroy Game deck" do
    visit game_deck_url(@game_deck)
    click_on "Destroy this game deck", match: :first

    assert_text "Game deck was successfully destroyed"
  end
end

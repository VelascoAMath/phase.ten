require "application_system_test_case"

class GameDiscardsTest < ApplicationSystemTestCase
  setup do
    @game_discard = game_discards(:one)
  end

  test "visiting the index" do
    visit game_discards_url
    assert_selector "h1", text: "Game discards"
  end

  test "should create game discard" do
    visit game_discards_url
    click_on "New game discard"

    fill_in "Card", with: @game_discard.card_id
    fill_in "Game", with: @game_discard.game_id
    fill_in "Order", with: @game_discard.order
    click_on "Create Game discard"

    assert_text "Game discard was successfully created"
    click_on "Back"
  end

  test "should update Game discard" do
    visit game_discard_url(@game_discard)
    click_on "Edit this game discard", match: :first

    fill_in "Card", with: @game_discard.card_id
    fill_in "Game", with: @game_discard.game_id
    fill_in "Order", with: @game_discard.order
    click_on "Update Game discard"

    assert_text "Game discard was successfully updated"
    click_on "Back"
  end

  test "should destroy Game discard" do
    visit game_discard_url(@game_discard)
    click_on "Destroy this game discard", match: :first

    assert_text "Game discard was successfully destroyed"
  end
end

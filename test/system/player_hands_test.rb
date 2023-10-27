require "application_system_test_case"

class PlayerHandsTest < ApplicationSystemTestCase
  setup do
    @player_hand = player_hands(:one)
  end

  test "visiting the index" do
    visit player_hands_url
    assert_selector "h1", text: "Player hands"
  end

  test "should create player hand" do
    visit player_hands_url
    click_on "New player hand"

    fill_in "Card", with: @player_hand.card_id
    fill_in "Game", with: @player_hand.game_id
    fill_in "Order", with: @player_hand.order
    fill_in "Player", with: @player_hand.player_id
    click_on "Create Player hand"

    assert_text "Player hand was successfully created"
    click_on "Back"
  end

  test "should update Player hand" do
    visit player_hand_url(@player_hand)
    click_on "Edit this player hand", match: :first

    fill_in "Card", with: @player_hand.card_id
    fill_in "Game", with: @player_hand.game_id
    fill_in "Order", with: @player_hand.order
    fill_in "Player", with: @player_hand.player_id
    click_on "Update Player hand"

    assert_text "Player hand was successfully updated"
    click_on "Back"
  end

  test "should destroy Player hand" do
    visit player_hand_url(@player_hand)
    click_on "Destroy this player hand", match: :first

    assert_text "Player hand was successfully destroyed"
  end
end

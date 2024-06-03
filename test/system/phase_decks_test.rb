require "application_system_test_case"

class PhaseDecksTest < ApplicationSystemTestCase
  setup do
    @phase_deck = phase_decks(:one)
  end

  test "visiting the index" do
    visit phase_decks_url
    assert_selector "h1", text: "Phase decks"
  end

  test "should create phase deck" do
    visit phase_decks_url
    click_on "New phase deck"

    fill_in "Card", with: @phase_deck.card_id
    fill_in "Game", with: @phase_deck.game_id
    fill_in "Order", with: @phase_deck.order
    fill_in "Player", with: @phase_deck.player_id
    click_on "Create Phase deck"

    assert_text "Phase deck was successfully created"
    click_on "Back"
  end

  test "should update Phase deck" do
    visit phase_deck_url(@phase_deck)
    click_on "Edit this phase deck", match: :first

    fill_in "Card", with: @phase_deck.card_id
    fill_in "Game", with: @phase_deck.game_id
    fill_in "Order", with: @phase_deck.order
    fill_in "Player", with: @phase_deck.player_id
    click_on "Update Phase deck"

    assert_text "Phase deck was successfully updated"
    click_on "Back"
  end

  test "should destroy Phase deck" do
    visit phase_deck_url(@phase_deck)
    click_on "Destroy this phase deck", match: :first

    assert_text "Phase deck was successfully destroyed"
  end
end

require "test_helper"

class PhaseDecksControllerTest < ActionDispatch::IntegrationTest
  setup do
    @phase_deck = phase_decks(:one)
  end

  test "should get index" do
    get phase_decks_url
    assert_response :success
  end

  test "should get new" do
    get new_phase_deck_url
    assert_response :success
  end

  test "should create phase_deck" do
    assert_difference("PhaseDeck.count") do
      post phase_decks_url, params: { phase_deck: { card_id: @phase_deck.card_id, game_id: @phase_deck.game_id, order: @phase_deck.order, player_id: @phase_deck.player_id } }
    end

    assert_redirected_to phase_deck_url(PhaseDeck.last)
  end

  test "should show phase_deck" do
    get phase_deck_url(@phase_deck)
    assert_response :success
  end

  test "should get edit" do
    get edit_phase_deck_url(@phase_deck)
    assert_response :success
  end

  test "should update phase_deck" do
    patch phase_deck_url(@phase_deck), params: { phase_deck: { card_id: @phase_deck.card_id, game_id: @phase_deck.game_id, order: @phase_deck.order, player_id: @phase_deck.player_id } }
    assert_redirected_to phase_deck_url(@phase_deck)
  end

  test "should destroy phase_deck" do
    assert_difference("PhaseDeck.count", -1) do
      delete phase_deck_url(@phase_deck)
    end

    assert_redirected_to phase_decks_url
  end
end

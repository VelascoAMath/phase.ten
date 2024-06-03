require "test_helper"

class GameDecksControllerTest < ActionDispatch::IntegrationTest
  setup do
    @game_deck = game_decks(:one)
  end

  test "should get index" do
    get game_decks_url
    assert_response :success
  end

  test "should get new" do
    get new_game_deck_url
    assert_response :success
  end

  test "should create game_deck" do
    assert_difference("GameDeck.count") do
      post game_decks_url, params: { game_deck: { card_id: @game_deck.card_id, game_id: @game_deck.game_id, order: @game_deck.order } }
    end

    assert_redirected_to game_deck_url(GameDeck.last)
  end

  test "should show game_deck" do
    get game_deck_url(@game_deck)
    assert_response :success
  end

  test "should get edit" do
    get edit_game_deck_url(@game_deck)
    assert_response :success
  end

  test "should update game_deck" do
    patch game_deck_url(@game_deck), params: { game_deck: { card_id: @game_deck.card_id, game_id: @game_deck.game_id, order: @game_deck.order } }
    assert_redirected_to game_deck_url(@game_deck)
  end

  test "should destroy game_deck" do
    assert_difference("GameDeck.count", -1) do
      delete game_deck_url(@game_deck)
    end

    assert_redirected_to game_decks_url
  end
end

require "test_helper"

class PlayerHandsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @player_hand = player_hands(:one)
  end

  test "should get index" do
    get player_hands_url
    assert_response :success
  end

  test "should get new" do
    get new_player_hand_url
    assert_response :success
  end

  test "should create player_hand" do
    assert_difference("PlayerHand.count") do
      post player_hands_url, params: { player_hand: { card_id: @player_hand.card_id, game_id: @player_hand.game_id, order: @player_hand.order, player_id: @player_hand.player_id } }
    end

    assert_redirected_to player_hand_url(PlayerHand.last)
  end

  test "should show player_hand" do
    get player_hand_url(@player_hand)
    assert_response :success
  end

  test "should get edit" do
    get edit_player_hand_url(@player_hand)
    assert_response :success
  end

  test "should update player_hand" do
    patch player_hand_url(@player_hand), params: { player_hand: { card_id: @player_hand.card_id, game_id: @player_hand.game_id, order: @player_hand.order, player_id: @player_hand.player_id } }
    assert_redirected_to player_hand_url(@player_hand)
  end

  test "should destroy player_hand" do
    assert_difference("PlayerHand.count", -1) do
      delete player_hand_url(@player_hand)
    end

    assert_redirected_to player_hands_url
  end
end

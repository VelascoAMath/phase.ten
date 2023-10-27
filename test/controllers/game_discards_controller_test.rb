require "test_helper"

class GameDiscardsControllerTest < ActionDispatch::IntegrationTest
  setup do
    @game_discard = game_discards(:one)
  end

  test "should get index" do
    get game_discards_url
    assert_response :success
  end

  test "should get new" do
    get new_game_discard_url
    assert_response :success
  end

  test "should create game_discard" do
    assert_difference("GameDiscard.count") do
      post game_discards_url, params: { game_discard: { card_id: @game_discard.card_id, game_id: @game_discard.game_id, order: @game_discard.order } }
    end

    assert_redirected_to game_discard_url(GameDiscard.last)
  end

  test "should show game_discard" do
    get game_discard_url(@game_discard)
    assert_response :success
  end

  test "should get edit" do
    get edit_game_discard_url(@game_discard)
    assert_response :success
  end

  test "should update game_discard" do
    patch game_discard_url(@game_discard), params: { game_discard: { card_id: @game_discard.card_id, game_id: @game_discard.game_id, order: @game_discard.order } }
    assert_redirected_to game_discard_url(@game_discard)
  end

  test "should destroy game_discard" do
    assert_difference("GameDiscard.count", -1) do
      delete game_discard_url(@game_discard)
    end

    assert_redirected_to game_discards_url
  end
end

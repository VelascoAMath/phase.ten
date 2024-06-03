require "test_helper"

class PlayerOrdersControllerTest < ActionDispatch::IntegrationTest
  setup do
    @player_order = player_orders(:one)
  end

  test "should get index" do
    get player_orders_url
    assert_response :success
  end

  test "should get new" do
    get new_player_order_url
    assert_response :success
  end

  test "should create player_order" do
    assert_difference("PlayerOrder.count") do
      post player_orders_url, params: { player_order: { game_id: @player_order.game_id, order: @player_order.order, player_id: @player_order.player_id } }
    end

    assert_redirected_to player_order_url(PlayerOrder.last)
  end

  test "should show player_order" do
    get player_order_url(@player_order)
    assert_response :success
  end

  test "should get edit" do
    get edit_player_order_url(@player_order)
    assert_response :success
  end

  test "should update player_order" do
    patch player_order_url(@player_order), params: { player_order: { game_id: @player_order.game_id, order: @player_order.order, player_id: @player_order.player_id } }
    assert_redirected_to player_order_url(@player_order)
  end

  test "should destroy player_order" do
    assert_difference("PlayerOrder.count", -1) do
      delete player_order_url(@player_order)
    end

    assert_redirected_to player_orders_url
  end
end

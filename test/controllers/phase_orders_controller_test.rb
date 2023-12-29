require "test_helper"

class PhaseOrdersControllerTest < ActionDispatch::IntegrationTest
  setup do
    @phase_order = phase_orders(:one)
  end

  test "should get index" do
    get phase_orders_url
    assert_response :success
  end

  test "should get new" do
    get new_phase_order_url
    assert_response :success
  end

  test "should create phase_order" do
    assert_difference("PhaseOrder.count") do
      post phase_orders_url, params: { phase_order: { game_id: @phase_order.game_id, order: @phase_order.order, player_id: @phase_order.player_id } }
    end

    assert_redirected_to phase_order_url(PhaseOrder.last)
  end

  test "should show phase_order" do
    get phase_order_url(@phase_order)
    assert_response :success
  end

  test "should get edit" do
    get edit_phase_order_url(@phase_order)
    assert_response :success
  end

  test "should update phase_order" do
    patch phase_order_url(@phase_order), params: { phase_order: { game_id: @phase_order.game_id, order: @phase_order.order, player_id: @phase_order.player_id } }
    assert_redirected_to phase_order_url(@phase_order)
  end

  test "should destroy phase_order" do
    assert_difference("PhaseOrder.count", -1) do
      delete phase_order_url(@phase_order)
    end

    assert_redirected_to phase_orders_url
  end
end

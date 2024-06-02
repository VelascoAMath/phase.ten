require "application_system_test_case"

class PlayerOrdersTest < ApplicationSystemTestCase
  setup do
    @player_order = player_orders(:one)
  end

  test "visiting the index" do
    visit player_orders_url
    assert_selector "h1", text: "Player orders"
  end

  test "should create player order" do
    visit player_orders_url
    click_on "New player order"

    fill_in "Game", with: @player_order.game_id
    fill_in "Order", with: @player_order.order
    fill_in "Player", with: @player_order.player_id
    click_on "Create Player order"

    assert_text "Player order was successfully created"
    click_on "Back"
  end

  test "should update Player order" do
    visit player_order_url(@player_order)
    click_on "Edit this player order", match: :first

    fill_in "Game", with: @player_order.game_id
    fill_in "Order", with: @player_order.order
    fill_in "Player", with: @player_order.player_id
    click_on "Update Player order"

    assert_text "Player order was successfully updated"
    click_on "Back"
  end

  test "should destroy Player order" do
    visit player_order_url(@player_order)
    click_on "Destroy this player order", match: :first

    assert_text "Player order was successfully destroyed"
  end
end

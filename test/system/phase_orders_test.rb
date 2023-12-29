require "application_system_test_case"

class PhaseOrdersTest < ApplicationSystemTestCase
  setup do
    @phase_order = phase_orders(:one)
  end

  test "visiting the index" do
    visit phase_orders_url
    assert_selector "h1", text: "Phase orders"
  end

  test "should create phase order" do
    visit phase_orders_url
    click_on "New phase order"

    fill_in "Game", with: @phase_order.game_id
    fill_in "Order", with: @phase_order.order
    fill_in "Player", with: @phase_order.player_id
    click_on "Create Phase order"

    assert_text "Phase order was successfully created"
    click_on "Back"
  end

  test "should update Phase order" do
    visit phase_order_url(@phase_order)
    click_on "Edit this phase order", match: :first

    fill_in "Game", with: @phase_order.game_id
    fill_in "Order", with: @phase_order.order
    fill_in "Player", with: @phase_order.player_id
    click_on "Update Phase order"

    assert_text "Phase order was successfully updated"
    click_on "Back"
  end

  test "should destroy Phase order" do
    visit phase_order_url(@phase_order)
    click_on "Destroy this phase order", match: :first

    assert_text "Phase order was successfully destroyed"
  end
end

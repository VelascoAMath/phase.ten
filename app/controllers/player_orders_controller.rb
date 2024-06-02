class PlayerOrdersController < ApplicationController
  before_action :set_player_order, only: %i[ show edit update destroy ]

  # GET /player_orders or /player_orders.json
  def index
    @player_orders = PlayerOrder.all
  end

  # GET /player_orders/1 or /player_orders/1.json
  def show
  end

  # GET /player_orders/new
  def new
    @player_order = PlayerOrder.new
  end

  # GET /player_orders/1/edit
  def edit
  end

  # POST /player_orders or /player_orders.json
  def create
    @player_order = PlayerOrder.new(player_order_params)

    respond_to do |format|
      if @player_order.save
        format.html { redirect_to player_order_url(@player_order), notice: "Player order was successfully created." }
        format.json { render :show, status: :created, location: @player_order }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @player_order.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /player_orders/1 or /player_orders/1.json
  def update
    respond_to do |format|
      if @player_order.update(player_order_params)
        format.html { redirect_to player_order_url(@player_order), notice: "Player order was successfully updated." }
        format.json { render :show, status: :ok, location: @player_order }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @player_order.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /player_orders/1 or /player_orders/1.json
  def destroy
    @player_order.destroy!

    respond_to do |format|
      format.html { redirect_to player_orders_url, notice: "Player order was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_player_order
      @player_order = PlayerOrder.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def player_order_params
      params.require(:player_order).permit(:game_id, :player_id, :order)
    end
end

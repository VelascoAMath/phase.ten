class PlayerHandsController < ApplicationController
  before_action :set_player_hand, only: %i[ show edit update destroy ]

  # GET /player_hands or /player_hands.json
  def index
    @player_hands = PlayerHand.all
  end

  # GET /player_hands/1 or /player_hands/1.json
  def show
  end

  # GET /player_hands/new
  def new
    @player_hand = PlayerHand.new
  end

  # GET /player_hands/1/edit
  def edit
  end

  # POST /player_hands or /player_hands.json
  def create
    @player_hand = PlayerHand.new(player_hand_params)

    respond_to do |format|
      if @player_hand.save
        format.html { redirect_to player_hand_url(@player_hand), notice: "Player hand was successfully created." }
        format.json { render :show, status: :created, location: @player_hand }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @player_hand.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /player_hands/1 or /player_hands/1.json
  def update
    respond_to do |format|
      if @player_hand.update(player_hand_params)
        format.html { redirect_to player_hand_url(@player_hand), notice: "Player hand was successfully updated." }
        format.json { render :show, status: :ok, location: @player_hand }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @player_hand.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /player_hands/1 or /player_hands/1.json
  def destroy
    @player_hand.destroy!

    respond_to do |format|
      format.html { redirect_to player_hands_url, notice: "Player hand was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_player_hand
      @player_hand = PlayerHand.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def player_hand_params
      params.require(:player_hand).permit(:game_id, :player_id, :card_id, :order)
    end
end

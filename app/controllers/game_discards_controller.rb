class GameDiscardsController < ApplicationController
  before_action :set_game_discard, only: %i[ show edit update destroy ]

  # GET /game_discards or /game_discards.json
  def index
    @game_discards = GameDiscard.all
  end

  # GET /game_discards/1 or /game_discards/1.json
  def show
  end

  # GET /game_discards/new
  def new
    @game_discard = GameDiscard.new
  end

  # GET /game_discards/1/edit
  def edit
  end

  # POST /game_discards or /game_discards.json
  def create
    @game_discard = GameDiscard.new(game_discard_params)

    respond_to do |format|
      if @game_discard.save
        format.html { redirect_to game_discard_url(@game_discard), notice: "Game discard was successfully created." }
        format.json { render :show, status: :created, location: @game_discard }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @game_discard.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /game_discards/1 or /game_discards/1.json
  def update
    respond_to do |format|
      if @game_discard.update(game_discard_params)
        format.html { redirect_to game_discard_url(@game_discard), notice: "Game discard was successfully updated." }
        format.json { render :show, status: :ok, location: @game_discard }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @game_discard.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /game_discards/1 or /game_discards/1.json
  def destroy
    @game_discard.destroy!

    respond_to do |format|
      format.html { redirect_to game_discards_url, notice: "Game discard was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_game_discard
      @game_discard = GameDiscard.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def game_discard_params
      params.require(:game_discard).permit(:game_id, :card_id, :order)
    end
end

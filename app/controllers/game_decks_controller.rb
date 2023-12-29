class GameDecksController < ApplicationController
  before_action :set_game_deck, only: %i[ show edit update destroy ]

  # GET /game_decks or /game_decks.json
  def index
    @game_decks = GameDeck.all
  end

  # GET /game_decks/1 or /game_decks/1.json
  def show
  end

  # GET /game_decks/new
  def new
    @game_deck = GameDeck.new
  end

  # GET /game_decks/1/edit
  def edit
  end

  # POST /game_decks or /game_decks.json
  def create
    @game_deck = GameDeck.new(game_deck_params)

    respond_to do |format|
      if @game_deck.save
        format.html { redirect_to game_deck_url(@game_deck), notice: "Game deck was successfully created." }
        format.json { render :show, status: :created, location: @game_deck }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @game_deck.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /game_decks/1 or /game_decks/1.json
  def update
    respond_to do |format|
      if @game_deck.update(game_deck_params)
        format.html { redirect_to game_deck_url(@game_deck), notice: "Game deck was successfully updated." }
        format.json { render :show, status: :ok, location: @game_deck }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @game_deck.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /game_decks/1 or /game_decks/1.json
  def destroy
    @game_deck.destroy!

    respond_to do |format|
      format.html { redirect_to game_decks_url, notice: "Game deck was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_game_deck
      @game_deck = GameDeck.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def game_deck_params
      params.require(:game_deck).permit(:game_id, :card_id, :order)
    end
end

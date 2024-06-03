class PhaseDecksController < ApplicationController
  before_action :set_phase_deck, only: %i[ show edit update destroy ]

  # GET /phase_decks or /phase_decks.json
  def index
    @phase_decks = PhaseDeck.all
  end

  # GET /phase_decks/1 or /phase_decks/1.json
  def show
  end

  # GET /phase_decks/new
  def new
    @phase_deck = PhaseDeck.new
  end

  # GET /phase_decks/1/edit
  def edit
  end

  # POST /phase_decks or /phase_decks.json
  def create
    @phase_deck = PhaseDeck.new(phase_deck_params)

    respond_to do |format|
      if @phase_deck.save
        format.html { redirect_to phase_deck_url(@phase_deck), notice: "Phase deck was successfully created." }
        format.json { render :show, status: :created, location: @phase_deck }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @phase_deck.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /phase_decks/1 or /phase_decks/1.json
  def update
    respond_to do |format|
      if @phase_deck.update(phase_deck_params)
        format.html { redirect_to phase_deck_url(@phase_deck), notice: "Phase deck was successfully updated." }
        format.json { render :show, status: :ok, location: @phase_deck }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @phase_deck.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /phase_decks/1 or /phase_decks/1.json
  def destroy
    @phase_deck.destroy!

    respond_to do |format|
      format.html { redirect_to phase_decks_url, notice: "Phase deck was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_phase_deck
      @phase_deck = PhaseDeck.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def phase_deck_params
      params.require(:phase_deck).permit(:game_id, :player_id, :card_id, :order)
    end
end

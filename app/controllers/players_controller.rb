class PlayersController < ApplicationController
  before_action :set_player, only: %i[ show edit update destroy ]
  skip_forgery_protection

  # GET /players or /players.json
  def index
    @players = Player.all
    
    render json: @players
  end

  # GET /players/1 or /players/1.json
  def show

    render json: {
      "player": @player,
      "hand": @player_hand
    }
  end

  # GET /players/new
  def new
    @player = Player.new
  end

  # GET /players/1/edit
  def edit
  end

  # POST /players or /players.json
  def create
    @player = Player.new(user_name:params["user_name"], display_name:params["display_name"],
    password:params["password"], password_confirmation:params["password_confirmation"])

    respond_to do |format|
      if @player.save
        format.html { redirect_to player_url(@player), notice: "Player was successfully created." }
        format.json { render :show, status: :created, location: @player }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @player.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /players/1 or /players/1.json
  def update
    respond_to do |format|
      if @player.update(player_params)
        format.html { redirect_to player_url(@player), notice: "Player was successfully updated." }
        format.json { render :show, status: :ok, location: @player }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @player.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /players/1 or /players/1.json
  def destroy
    @player.destroy!

    respond_to do |format|
      format.html { redirect_to players_url, notice: "Player was successfully destroyed." }
      format.json { head :no_content }
    end
  end
  private

  def set_player
    @player = Player.find(params[:id])
    @player_hand = Player.find(params[:id]).player_hands
  end


  def user_params
    params.require(:player).permit(:user_name, :display_name, :password, :password_confirmation)
  end
end

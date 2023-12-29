class CardsController < ApplicationController
  skip_forgery_protection


  # GET /cards or /cards.json
  def index
    @cards = Card.all
    render json: @cards
  end

  # GET /cards/1 or /cards/1.json
  def show
    @card = Card.find(params[:id])

  end

  # GET /cards/new
  def create
    Rails.logger.info("--------------------")
    rank = params[:rank].downcase
    color = params[:color].downcase
    @card = Card.new(rank: rank, color: color)
    @card.save!
    
    render json: @card, status: 200
  end


  def delete_all
    Card.delete(Card.all)
  end

end

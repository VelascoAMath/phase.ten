class PhaseOrdersController < ApplicationController
  before_action :set_phase_order, only: %i[ show edit update destroy ]

  # GET /phase_orders or /phase_orders.json
  def index
    @phase_orders = PhaseOrder.all
  end

  # GET /phase_orders/1 or /phase_orders/1.json
  def show
  end

  # GET /phase_orders/new
  def new
    @phase_order = PhaseOrder.new
  end

  # GET /phase_orders/1/edit
  def edit
  end

  # POST /phase_orders or /phase_orders.json
  def create
    @phase_order = PhaseOrder.new(phase_order_params)

    respond_to do |format|
      if @phase_order.save
        format.html { redirect_to phase_order_url(@phase_order), notice: "Phase order was successfully created." }
        format.json { render :show, status: :created, location: @phase_order }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @phase_order.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /phase_orders/1 or /phase_orders/1.json
  def update
    respond_to do |format|
      if @phase_order.update(phase_order_params)
        format.html { redirect_to phase_order_url(@phase_order), notice: "Phase order was successfully updated." }
        format.json { render :show, status: :ok, location: @phase_order }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @phase_order.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /phase_orders/1 or /phase_orders/1.json
  def destroy
    @phase_order.destroy!

    respond_to do |format|
      format.html { redirect_to phase_orders_url, notice: "Phase order was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_phase_order
      @phase_order = PhaseOrder.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def phase_order_params
      params.require(:phase_order).permit(:game_id, :player_id, :order)
    end
end

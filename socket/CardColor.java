public enum CardColor {
    RED,
    BLUE,
    GREEN,
    YELLOW,
    WILD,
    SKIP;

    @Override
    public String toString() {
        switch (this){
            case RED -> {
                return "R";
            }
            case BLUE -> {
                return "B";
            }
            case GREEN -> {
                return "G";
            } case YELLOW -> {
                return "Y";
            } case  WILD -> {
                return "W";
            } case SKIP -> {
                return "S";
            }
            default -> throw new IllegalStateException("Unexpected value: " + this);
        }
    }
}

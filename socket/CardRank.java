public enum CardRank {
    ONE,
    TWO,
    THREE,
    FOUR,
    FIVE,
    SIX,
    SEVEN,
    EIGHT,
    NINE,
    TEN,
    ELEVEN,
    TWELVE,
    SKIP,
    WILD;

    @Override
    public String toString() {
        switch (this){
            case ONE -> {
                return "1";
            }
            case TWO -> {
                return "2";
            }
            case THREE -> {
                return "3";
            }
            case FOUR -> {
                return "4";
            }
            case FIVE -> {
                return "5";
            }
            case SIX -> {
                return "6";
            }
            case SEVEN -> {
                return "7";
            }
            case EIGHT -> {
                return "8";
            }
            case NINE -> {
                return "9";
            }
            case TEN -> {
                return "10";
            }
            case ELEVEN -> {
                return "11";
            }
            case TWELVE -> {
                return "12";
            }
            case WILD -> {
                return "W";
            }
            case SKIP -> {
                return "S";
            }

            default -> throw new IllegalStateException("Unexpected value: " + this);
        }
    }
}

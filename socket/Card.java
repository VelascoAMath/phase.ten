import java.util.ArrayList;
import java.util.Collections;
import java.util.List;


public class Card implements Comparable{

    private final CardColor color;

    private final CardRank rank;

    public Card(CardColor c, CardRank r) throws Exception {
        if(c == null){
            throw new NullPointerException("CardColor cannot be null!");
        }
        if(r == null){
            throw new NullPointerException("CardRank cannot be null!");
        }

        color = c;
        rank = r;

        if((c == CardColor.WILD && r != CardRank.WILD) || ((c != CardColor.WILD && r == CardRank.WILD))){
            throw new Exception(String.format("Both rank(%s) and color(%s) must be wild if one of them is wild!", c, r) );
        }
        if((c == CardColor.SKIP && r != CardRank.SKIP) || ((c != CardColor.SKIP && r == CardRank.SKIP))){
            throw new Exception(String.format("Both rank(%s) and color(%s) must be skip if one of them is skip!", c, r));
        }
    }

    public static Card createSkip(){
        try {
            return new Card(CardColor.SKIP, CardRank.SKIP);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static Card createWild() {
        try {
            return new Card(CardColor.WILD, CardRank.WILD);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args) throws Exception {
        ArrayList<Card> deck = (ArrayList<Card>) createDeck();
        Collections.shuffle(deck);
        System.out.println(deck);
    }


    @Override
    public boolean equals(Object obj) {
        if(obj instanceof Card other){
            return other.getRank() == getRank() && other.getColor() == getColor();
        } else {
            return false;
        }
    }

    @Override
    public int compareTo(Object o) {
        if(o == null){
            throw new NullPointerException("Can't compare with null!");
        }
        if(o instanceof Card other){
            if(other.getColor() == getColor()){
                return getRank().compareTo(other.getRank());
            } else {
                return getColor().compareTo(other.getColor());
            }
        } else {
            return 0;
        }
    }

    public CardRank getRank() {
        return rank;
    }

    @Override
    public String toString() {
        if(rank == CardRank.WILD)
            return "W";
        if(rank == CardRank.SKIP)
            return "S";
        return color.toString() + rank;
    }

    public static List<Card> getCollectionFromString(String s) throws Exception {
        BArrayList<Card> result = new BArrayList<>();
        for(String i: s.split(" ")){
            if(i.equals("W")) {
                result.add(Card.createWild());
                continue;
            }
            if(i.equals("S")){
                result.add(createSkip());
                continue;
            }
            if(!i.matches("[BRYG][\\dWS]+")){
                throw new Exception(String.format("Card %s needs to match [BRYG][\\dWS]+ but it doesn't!", i));
            }
            CardColor color;
            CardRank rank;
            color = switch (i.charAt(0)) {
                case 'B' -> CardColor.BLUE;
                case 'R' -> CardColor.RED;
                case 'Y' -> CardColor.YELLOW;
                case 'G' -> CardColor.GREEN;
                default -> throw new Exception(String.format("Unrecognized color %s", i.charAt(0)));
            };


            rank = switch (i.substring(1)) {
                case "1" -> CardRank.ONE;
                case "2" -> CardRank.TWO;
                case "3" -> CardRank.THREE;
                case "4" -> CardRank.FOUR;
                case "5" -> CardRank.FIVE;
                case "6" -> CardRank.SIX;
                case "7" -> CardRank.SEVEN;
                case "8" -> CardRank.EIGHT;
                case "9" -> CardRank.NINE;
                case "10" -> CardRank.TEN;
                case "11" -> CardRank.ELEVEN;
                case "12" -> CardRank.TWELVE;
                default -> throw new Exception(String.format("Unrecognized number %s", i.substring(1)));
            };

            result.add(new Card(color, rank));

        }
        return result;
    }


    public static List<Card> createDeck() throws Exception {
        BArrayList<Card> deck = new BArrayList<>();
        for (CardColor c: CardColor.values()) {
            if(c == CardColor.WILD || c == CardColor.SKIP)
                continue;
            for(CardRank r: CardRank.values()){
                if(r == CardRank.WILD || r == CardRank.SKIP)
                    continue;
                deck.add(new Card(c, r));
                deck.add(new Card(c, r));
            }
        }

        for(int i = 0; i < 4; i++){
            deck.add(createSkip());
        }
        for(int i = 0; i < 8; i++){
            deck.add(createWild());
        }
        return deck;
    }

    public CardColor getColor() {
        return color;
    }

}

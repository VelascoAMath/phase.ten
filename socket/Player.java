import java.util.Comparator;

public class Player {

    private final BArrayList<Card> hand;
    private final BArrayList<Card> skipList;

    private String name;

    private int phase;

    public Player(BArrayList<Card> hand, String name, int phase) {
        this.hand = hand;
        this.name = name;
        this.phase = phase;
        skipList = new BArrayList<>(0);
    }

    @Override
    public String toString() {
        return "Player{" +
                "hand=" + hand +
                ", skip=" + skipList.size() +
                ", name='" + name + '\'' +
                ", phase=" + phase +
                '}';
    }

    public int getNumCards () { return hand.size(); }

    public void addCard(Card c){ hand.add(c);}

    public void setPhase(int phase) {
        this.phase = phase;
    }

    public void incrementPhase(){ this.phase++; }

    public boolean hasSkip(){
        return !skipList.isEmpty();
    }

    public boolean hasSkipInHand() {
        try {
            return  hand.contains(new Card(CardColor.SKIP, CardRank.SKIP));

        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public Card popSkip(){
        return skipList.removeLast();
    }

    public boolean hasCard(String selection) {
        try{
            BArrayList<Card> cardList = (BArrayList<Card>) Card.getCollectionFromString(selection);
            if (cardList.size() != 1)
                return false;
            Card c = cardList.getFirst();
            return hand.contains(c);
        } catch (Exception e) {
            return false;
        }
    }

    public Card removeCard(String selection) throws Exception {
        BArrayList<Card> cardList = (BArrayList<Card>) Card.getCollectionFromString(selection);
        if (cardList.size() != 1)
            throw new Exception("Can only remove one card!");
        Card c = cardList.getFirst();
        Card result = hand.get(hand.indexOf(c));
        hand.remove(c);
        return result;

    }

    public void sortByRank() {
        hand.sort(Comparator.comparing(Card::getRank));
    }

    public void sortByColor() {
        hand.sort(Comparator.comparing(Card::getColor));
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public int getPhase() {
        return phase;
    }

    public BArrayList<Card> getHand() {
        return hand;
    }

    public BArrayList<Card> getSkipList() {
        return skipList;
    }
}

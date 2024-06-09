import java.io.PrintWriter;
import java.util.*;


/**
 * This class is a custom Regular Expression that we created specifically to determine if a phase has been achieved by a player
 */
public class RE {

    private static class State {

        @Override
        public String toString() {
            return "State{" +
                    (isFinal? "isFinal,": "") +
                    (cardTransition.isEmpty()? "": "card:" + cardTransition.keySet()) +
                    (rankTransition.isEmpty()? "": "rank:" + rankTransition.keySet()) +
                    (colorTransition.isEmpty()? "": "color:" + colorTransition.keySet()) +
                    (defaultTransition == null? "": "defaultTransition") +
                    (emptyTransition == null? "": "emptyTransition") +
                    '}';
        }

        boolean isFinal = false;
        HashMap<Card, State> cardTransition = new HashMap<>();
        HashMap<CardRank, State> rankTransition = new HashMap<>();
        HashMap<CardColor, State>  colorTransition = new HashMap<>();

        State defaultTransition = null;
        State emptyTransition = null;

        public boolean isAccepted(Card c){
            return cardTransition.containsKey( c) || rankTransition.containsKey(c.getRank()) || colorTransition.containsKey(c.getColor()) || defaultTransition != null || emptyTransition != null;
        }

        public State getNext(Card c) {
            if (emptyTransition != null)
                return emptyTransition;

            if(cardTransition.containsKey(c))
                return cardTransition.get(c);
            if(rankTransition.containsKey(c.getRank()))
                return rankTransition.get(c.getRank());
            if(colorTransition.containsKey(c.getColor()))
                return colorTransition.get(c.getColor());

            if(defaultTransition == null)
                throw new IllegalArgumentException(c + " not in the transitions!");
            else
                return defaultTransition;
        }



        public void put(CardRank r, State state) {
            rankTransition.put(r, state);
        }
        public void put(CardColor c, State state) {
            colorTransition.put(c, state);
        }
        public void put(State state){ defaultTransition = state;}
    }

    private State startState;


    private String phase;

    public String getPhase() {
        return phase;
    }

    public RE(String phase) throws Exception {
        this.phase = phase;
        if(phase.equals("S")){
            startState = strictSet();
        } else if (phase.equals("C")) {
            startState = strictColor();
        } else if (phase.equals("R")){
            startState = strictRun();
        }
        else if (phase.matches("S\\d+")){

            Pair<State, List<State>> results = strictSet(Integer.parseInt(phase.substring(1)));

            startState = results.item1;
            List<State> endStates = results.item2;

            for(State s: endStates){
                s.isFinal = true;
            }
        }
        else if (phase.matches("C\\d+")){

            Pair<State, List<State>> results = strictColor(Integer.parseInt(phase.substring(1)));

            startState = results.item1;
            List<State> endStates = results.item2;

            for(State s: endStates){
                s.isFinal = true;
            }
        }
        else if (phase.matches("R\\d+")){

            Pair<State, List<State>> results = strictRun(Integer.parseInt(phase.substring(1)));

            startState = results.item1;
            List<State> endStates = results.item2;

            for(State s: endStates){
                s.isFinal = true;
            }
        } else if (phase.matches("(?:[CSR]\\d\\+)+[CSR]\\d")){
            BArrayList<Pair<State, List<State>>> reList = new BArrayList<>();
            for(String comp: phase.split("\\+")){
                Pair<State, List<State>> result;
                if(comp.matches("C\\d+")){
                    result = strictColor(Integer.parseInt(comp.substring(1)));
                } else if (comp.matches("R\\d+")) {
                    result = strictRun(Integer.parseInt(comp.substring(1)));
                } else if (comp.matches("S\\d+")) {
                    result = strictSet(Integer.parseInt(comp.substring(1)));
                } else {
                    throw new Exception(String.format("Unexpected component %s", comp));
                }
                reList.add(result);
            }

            for(int i = 0; i < reList.size(); i++) {
                if(i == 0)
                    startState = reList.getFirst().item1;
                else {
                    List<State> endStates = reList.get(i-1).item2;
                    State nextState = reList.get(i).item1;
                    for(State end: endStates){
                        end.emptyTransition = nextState;
                    }
                }
            }

            for(State end: reList.getLast().item2){
                end.isFinal = true;
            }
        }
        else {
            throw new IllegalArgumentException(String.format("DO NOT RECOGNIZE %s!!!", phase));
        }
    }

    private State strictRun() {
        State start = new State();
        int n = CardRank.values().length - 2;
        State[] rankCards = new State[n];
        State[] wildCard = new State[n];
        for(int i = 0; i < n; i++){
            CardRank r = CardRank.values()[i];
            rankCards[i] = new State();
            wildCard[i] = new State();
            rankCards[i].isFinal = true;
            wildCard[i].isFinal = true;
            start.put(r, rankCards[i]);
            if(i > 0){
                rankCards[i-1].put(r, rankCards[i]);
                rankCards[i-1].put(CardRank.WILD, rankCards[i]);
                wildCard[i-1].put(CardRank.WILD, wildCard[i]);
            }
        }

        for(int i = 0; i < n - 1; i++){
            CardRank r = CardRank.values()[i];
            wildCard[i].put(r, rankCards[i]);
            for(int j = i + 1; j < n - 1; j++){
                CardRank r2 = CardRank.values()[j];
                wildCard[i].put(r2, rankCards[j]);
            }
        }

        start.put(CardRank.WILD, wildCard[0]);
        return start;
    }

    private Pair<State, List<State>> strictRun(int runSize){

        State beginState = new State();

        CardRank[] orderedValues = Arrays.copyOfRange(CardRank.values(), 0,
                CardRank.values().length - 2);

        ArrayList<State> endStateList = new ArrayList<>();
        ArrayList<BArrayList<State>> runStateTable = new ArrayList<>(orderedValues.length-runSize+1);

        for(int i = 0; i < orderedValues.length - runSize + 1; i++){
            BArrayList<State> runList = new BArrayList<>(runSize);
            for(int j = 0; j < runSize; j++){
                runList.add(new State());
            }
            runStateTable.add(runList);
            endStateList.add(runList.getLast());
            beginState.put(orderedValues[i], runList.getFirst());
        }
        for(int i = 0; i < orderedValues.length - runSize + 1; i++){
            for(int j = 1; j < runSize; j++){
                runStateTable.get(i).get(j-1).put(orderedValues[i+j], runStateTable.get(i).get(j) );
            }
        }

        BArrayList<State> wildCardList = new BArrayList<>(runSize);
        for(int i = 0; i < runSize; i++){
            wildCardList.add(i, new State());
            if(i > 0)
                wildCardList.get(i-1).put(CardRank.WILD, wildCardList.get(i));
        }

        endStateList.add(wildCardList.get(runSize-1));
        beginState.put(CardRank.WILD, wildCardList.get(0));

        for(int i = 0; i < runSize-1; i++){
            for(int j = 0; j < runStateTable.size(); j++){
                wildCardList.get(i).put(orderedValues[i+j+1], runStateTable.get(j).get(i+1));
            }
        }

        for (ArrayList<State> states : runStateTable) {
            for (int j = 1; j < states.size(); j++) {
                states.get(j - 1).put(CardRank.WILD, states.get(j));
            }
        }
        return new Pair<>(beginState, endStateList);
    }

    private Pair<State, List<State>> strictColor(int colorSize) {

        State beginState = new State();
        ArrayList<State> endStateList = new ArrayList<>();
        State[] wildList = new State[colorSize];
        for(int i = 0; i < colorSize; i++){
            wildList[i] = new State();
        }
        // Connect the wild cards to each other
        for(int i = 1; i < colorSize; i++){
            wildList[i-1].put(CardRank.WILD, wildList[i]);
        }
        // A collection of wild cards is technically a set
        wildList[colorSize-1].put(CardRank.WILD, wildList[colorSize-1]);

        beginState.put(CardRank.WILD, wildList[0]);

        for(CardColor c: CardColor.values()){

            State[] stateList = new State[colorSize];
            for(int i = 0; i < colorSize; i++){
                stateList[i] = new State();
                if(i > 0)
                    wildList[i-1].put(c, stateList[i]);
            }
            wildList[colorSize - 1].put(c, stateList[colorSize - 1]);
            // Start to the first card of the rank
            beginState.put(c, stateList[0]);
            // Connect the rank cards to each other;
            for(int i = 0; i < colorSize - 1; i++){
                stateList[i].put(c, stateList[i + 1]);
                stateList[i].put(CardRank.WILD, stateList[i + 1]);
            }
            stateList[colorSize - 1].put(c, stateList[colorSize - 1]);
            stateList[colorSize - 1].put(CardRank.WILD, stateList[colorSize - 1]);

            endStateList.add(stateList[colorSize - 1]);

        }

        return new Pair<>(beginState, endStateList);
    }

    private State strictColor() {
        State start = new State();

        State wildState = new State();
        start.put(CardRank.WILD, wildState);
        wildState.put(CardRank.WILD, wildState);
        wildState.isFinal = true;

        for(CardColor c: CardColor.values()){
            State s = new State();
            s.isFinal = true;
            start.put(c, s);
            s.put(c, s);
            s.put(CardRank.WILD, s);
            wildState.put(c, s);
        }

        return start;
    }

    private Pair<State, List<State>> strictSet(int setSize){

        State beginState = new State();
        ArrayList<State> endStateList = new ArrayList<>();
        State[] wildList = new State[setSize];
        for(int i = 0; i < setSize; i++){
            wildList[i] = new State();
        }
        // Connect the wild cards to each other
        for(int i = 1; i < setSize; i++){
            wildList[i-1].put(CardRank.WILD, wildList[i]);
        }
        // A collection of wild cards is technically a set
        wildList[setSize-1].put(CardRank.WILD, wildList[setSize-1]);

        beginState.put(CardRank.WILD, wildList[0]);

        for(CardRank r: CardRank.values()){
            if(r == CardRank.SKIP)
                continue;
            if (r == CardRank.WILD)
                continue;

            State[] stateList = new State[setSize];
            for(int i = 0; i < setSize; i++){
                stateList[i] = new State();
                if(i > 0)
                    wildList[i-1].put(r, stateList[i]);
            }
            wildList[setSize - 1].put(r, stateList[setSize - 1]);
            // Start to the first card of the rank
            beginState.put(r, stateList[0]);
            // Connect the rank cards to each other;
            for(int i = 0; i < setSize - 1; i++){
                stateList[i].put(r, stateList[i + 1]);
                stateList[i].put(CardRank.WILD, stateList[i + 1]);
            }
            stateList[setSize - 1].put(r, stateList[setSize - 1]);
            stateList[setSize - 1].put(CardRank.WILD, stateList[setSize - 1]);

            endStateList.add(stateList[setSize - 1]);

        }

        return new Pair<>(beginState, endStateList);
    }


    /**
     * Returns a State that examines if a player has set of cards
     * @return State
     */
    private State strictSet() {
        State beginState = new State();
        Map<CardRank, State> goodStateMap = new HashMap<>();

        // Create states for each number rank
        for(CardRank r: CardRank.values()){
            if(r == CardRank.SKIP || r == CardRank.WILD)
                continue;

            State goodState = new State();
            goodState.put(r, goodState);
            goodState.put(CardRank.WILD, goodState);
            goodStateMap.put(r, goodState);
            goodState.isFinal = true;
            // Start to the first card of the rank
            beginState.put(r, goodState);
            beginState.put(CardRank.WILD, goodState);

        }

        // Add the wildcard case
        State wildState = new State();
        wildState.isFinal = true;
        beginState.put(CardRank.WILD, wildState);
        wildState.put(CardRank.WILD, wildState);
        for(CardRank r: CardRank.values()){
            if(r == CardRank.WILD || r == CardRank.SKIP)
                continue;
            wildState.put(r, goodStateMap.get(r));
        }

        return beginState;
    }

    private boolean isRejected(ArrayList<Card> input) {
        State curr = startState;
        for(Card c: input){
            while(curr.emptyTransition != null)
                curr = curr.getNext(c);
            if(!curr.isAccepted(c))
                return false;

            curr = curr.getNext(c);
        }
        return true;
    }

    private boolean isAccepted(List<Card> input){
        State curr = startState;
        if(curr.isFinal)
            return true;
        for(Card c: input){
            while(curr.emptyTransition != null)
                curr = curr.getNext(c);
            if(!curr.isAccepted(c))
                return false;


            curr = curr.getNext(c);
            if(curr.isFinal)
                return true;
        }
        return curr.isFinal;
    }

    /***
     * Sees if the entirety of the hand of cards is accepted into the phase
     * @param input: The list of cards to check
     * @return boolean: is the entire collection of cards is accepted
     */
    public boolean isAcceptedFully(List<Card> input){
        State curr = startState;
        for(Card c: input){
            while(curr.emptyTransition != null)
                curr = curr.getNext(c);
            if(!curr.isAccepted(c))
                return false;

            curr = curr.getNext(c);
        }
        return curr.isFinal;
    }


    private static class IndexList {
        ArrayList<Integer> list;
        int n;


        public IndexList(int n) {
            list = new ArrayList<>();
            this.n = n;
        }

        public IndexList clone(){
            IndexList result = new IndexList(n);
            result.list = new ArrayList<>(list);
            return result;
        }

        public int size() {
            return list.size();
        }

        public boolean add(Integer integer) {
            return list.add(integer);
        }



        @Override
        public String toString() {
            return "IndexList{" +
                    "list=" + list +
                    '}';
        }

    }

    private static ArrayList<Card> get(List<Card> l, IndexList index){
        ArrayList<Card> result = new ArrayList<>();


        for(Integer i: index.list){
            result.add(l.get(i));
        }

        return result;
    }
    public boolean isAcceptedSubset(List<Card> input){


        IndexList l = new IndexList(input.size());
        LinkedList<IndexList> q = new LinkedList<>();
        q.add(l);

        while(!q.isEmpty()) {
            IndexList curr = q.removeFirst();
            if(!isRejected(get(input, curr)))
                continue;
            for (IndexList next: expandList(curr)) {
                q.addLast(next);
                if(isAcceptedFully(get(input, next)))
                    return true;
            }
        }

        return false;
    }



    private ArrayList<IndexList> expandList(IndexList indices) {
        if(indices.size() == indices.n)
            return new ArrayList<>();
        HashSet<Integer> occupied = new HashSet<>(indices.list);
        ArrayList<IndexList> result = new ArrayList<>();

        for(int i = 0; i < indices.n; i++){
            if (occupied.contains(i))
                continue;
            IndexList next = indices.clone();
            next.add(i);
            result.add(next);
        }
        return result;
    }

    public void printOutGraph() throws Exception {
        PrintWriter writer = new PrintWriter("RE.dot");
        LinkedList<State> q = new LinkedList<>();
        HashSet<State> visited = new HashSet<>();

        writer.println("digraph RE {");

        IdMap<State> stateToId = new IdMap<>();
        q.add(startState);
        visited.add(startState);
        while(!q.isEmpty()){
            State s = q.removeFirst();
            stateToId.add(s);
            writer.print("N" + stateToId.get(s) + "[label=\"\"]");
            if(s.isFinal){
                writer.print("[color=green]");
            } else if (s == startState) {
                writer.print("[color=blue, shape=square]");
            }
            writer.println(";");

            if(s.defaultTransition != null) {
                State next = s.defaultTransition;
                if (!visited.contains(next))
                    q.add(next);
                visited.add(next);
                stateToId.add(next);
                writer.printf("N%d->N%d;%n", stateToId.get(s), stateToId.get(next));
            }
            if(s.emptyTransition != null) {
                State next = s.emptyTransition;
                if (!visited.contains(next))
                    q.add(next);
                visited.add(next);
                stateToId.add(next);
                writer.printf("N%d->N%d;%n", stateToId.get(s), stateToId.get(next));
            }

            for(Map.Entry<Card, State> a: s.cardTransition.entrySet()){
                State next = a.getValue();
                if (!visited.contains(next))
                    q.add(next);
                visited.add(next);
                stateToId.add(next);
                writer.printf("N%d->N%d[label=%s];%n", stateToId.get(s), stateToId.get(next), a.getKey());
            }

            for(Map.Entry<CardRank, State> a: s.rankTransition.entrySet()){
                State next = a.getValue();
                if (!visited.contains(next))
                    q.add(next);
                visited.add(next);
                stateToId.add(next);
                writer.printf("N%d->N%d[label=%s];%n", stateToId.get(s), stateToId.get(next), a.getKey());
            }

            for(Map.Entry<CardColor, State> a: s.colorTransition.entrySet()){
                State next = a.getValue();
                if (!visited.contains(next))
                    q.add(next);
                visited.add(next);
                stateToId.add(next);
                writer.printf("N%d->N%d[label=%s];%n", stateToId.get(s), stateToId.get(next), a.getKey());
            }

        }

        writer.println("}");
        writer.close();

    }

    public static String[] generalizeRE(String re){
        String[] partList = re.split("\\+");
        for(int i = 0; i < partList.length; i++){
            partList[i] = partList[i].substring(0, 1);
        }
        return partList;
    }

//     public static void main(String[] args) throws Exception {
//         RE re = new RE("S5+S2");
// //        ArrayList<Card> l = (ArrayList<Card>) Card.getCollectionFromString("BW RW Y8 GW G8");
// //        ArrayList<Card> l = (ArrayList<Card>) Card.getCollectionFromString("Y8 R3 BW RW G9 G9 B8 YW B7 B1");
// //        ArrayList<Card> l = (ArrayList<Card>) Card.getCollectionFromString("W W W B4 G5 W G7 Y8");
//         ArrayList<Card> l = (ArrayList<Card>) Card.getCollectionFromString("W R1 G1 Y1 B1 Y2 B2 W");
//         System.out.println(l);
//         System.out.println(re.isAccepted(l));
//         System.out.println(re.isAcceptedFully(l));
//         System.out.println(re.isAcceptedSubset(l));
//         re.printOutGraph();
//     }

    public static void main(String[] args) throws Exception {
        String phase = null;
        ArrayList<String> deck = new ArrayList<String>();

        if(args.length == 0){

            System.out.println("Usage: java RE -p (phase) -d (card1) [card2] [card3] ...");
            System.out.println("Phases must be in the format ([CSR]\\d+)*[CSR]");
            System.out.println("The + isn't a regular expression +. It literally means +");
            System.out.println("Cards must be in the format [RBGY][0-9] or [RBGY]10 or [RBGY]11 or [RBGY]12 or W or S");
            System.exit(0);
        }

        for(int i = 0; i < args.length; i++){
            if(args[i].equals("-p")){
                phase = args[++i];
            } else if (args[i].equals("-d")){
                i++;
                for(;i < args.length; i++){
                    deck.add(args[i]);
                }
            }
        }

        if(phase == null){
            System.err.println("Phase has not been set!");
            System.exit(1);
        }
        if(deck.size() == 0){
            System.err.println("Deck has not been provided!");
            System.exit(1);
        }

        RE re = new RE(phase);
        ArrayList<Card> l = (ArrayList<Card>) Card.getCollectionFromString(String.join(" ", deck));
        System.out.println(re.isAcceptedFully(l));
    }
}

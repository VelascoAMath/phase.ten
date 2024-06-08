import { useParams } from "wouter";
import PlayerLogin from "./PlayerLogin";


const rankToColor = {
    "R": "red",
    "B": "blue",
    "Y": "yellow",
    "G": "green",
};

const getClassFromRank = function(rank) {
    if(rank === 'S'){
        return 'card skip';
    }
    if(rank === 'W'){
        return 'card wild';
    }
    return 'card';
}

const getDeckDivs = function(deck){
    return deck.map((card, idx) => {return <div style={{backgroundColor: rankToColor[card.color]}} key={idx} className={getClassFromRank(card.rank)}>{card.rank}</div>} );
}




export default function PlayRoom({props}) {
    const{state, dispatch, socket} = props;

	const params = useParams();
	const game_id = params?.id;
    const name = state["user-name"];
    const user_id = state["user-id"];
    const game = state["game-list"]?.filter(game => game.id === game_id)[0];

    if(game === undefined){
        return <div>{game_id} is not a valid game room!</div>
    }

    // Either we haven't made a call to get the player data
    if(state["player"] === undefined){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "get_player", "user_id": user_id, "game_id": game_id }));
        }
        return <div>Getting player data {socket.readyState} {JSON.stringify(state["player"])}</div>
    }
    // Or we have old player information
    if(state["player"]["game_id"] !== game_id || state["player"]["user_id"] !== user_id){

        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "get_player", "user_id": user_id, "game_id": game_id }));
            return <div>Getting player data {JSON.stringify(state["player"])}</div>
        }
    }

    const player = state["player"]["player"];
    if(player === undefined){
        return <div>
            <div>You are not a player in this game!</div>
            <div>{game_id}</div>
            <div>{user_id}</div>
            {JSON.stringify(state)}
            </div>
    }

    const hand = player["hand"];
    const player_id = player["id"];

    const drawDeck = function(){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "draw_deck", player_id: player_id}));
        }
    }


    const sortByColor = function(cardCollection){
        // cardCollection.sort((a, b) => {
        //     if(a.color < b.color) {
        //     return -1;   
        //     } if (a.color == b.color){
        //         return 0;
        //     } else {
        //         return 1;
        //     }
        // })

        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "sort_by_color", player_id: player_id}));
        }
    }
    const sortByRank = function(cardCollection){
        // const rankOrdering = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'W', 'S']
        // cardCollection.sort((a, b) => {
        //     const aIndex = rankOrdering.indexOf(a.rank);
        //     const bIndex = rankOrdering.indexOf(b.rank);
        //     if(aIndex < bIndex) {
        //     return -1;   
        //     } if (aIndex == bIndex){
        //         return 0;
        //     } else {
        //         return 1;
        //     }
        // })
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "sort_by_rank", player_id: player_id}));
        }
    }



    return (
        <div>
            <PlayerLogin  props={{state, dispatch, socket}}/>
            <div>
                User is {name} {user_id}
            </div>
            <div>
                Play room {game_id}
            </div>

            <div className="card-collection">
                {getDeckDivs(game["discard"]) }
            </div>
            <div className="card-collection">
                {getDeckDivs(player["hand"])}
            </div>
            <div className="player-console">
                <button onClick={() => {sortByRank(hand)}}>Sort by rank</button>
                <button onClick={() => {sortByColor(hand)}}>Sort by color</button>
                <button onClick={drawDeck}>Draw Deck</button>
            </div>
            <div>
                {JSON.stringify(player)}
            </div>
            <div className="card-collection">
                {getDeckDivs(game["deck"])}
            </div>
        </div>
    )
}
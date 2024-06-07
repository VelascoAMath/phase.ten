import { useParams } from "wouter";


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





    return (
        <div>
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
            <div>
                {JSON.stringify(player)}
            </div>
            <div>
                {JSON.stringify(game)}
            </div>
        </div>
    )
}
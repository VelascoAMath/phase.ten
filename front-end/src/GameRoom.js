import React from "react";
import Button from 'react-bootstrap/Button';


const joinGameButton = function(game, title, key, onClick){
    const nameList = game.users.map(user => {return <div key={user.id}>{user.name}</div>});
    
    return (
        <div style={{backgroundColor: "brown", cursor: "pointer"}} key={key} onClick={onClick}>
            {title}
            {nameList}
        </div>
    )
}

export default function PlayerPage({props}) {

    const{state, dispatch, socket} = props;

    if(!(state["user-id"] && state["user-token"])){
        return (
            <div>
                You must log in first!
            </div>
        )
    }


    if(socket.readyState === 1){
        socket.send(JSON.stringify({type: "get_games"}));
    }

    const createGame = function() {
        socket.send(JSON.stringify({type: "create_game", "user_id": state["user-id"] }));
    }

    const joinGame = function(game_id) {
        socket.send(JSON.stringify({type: "join_game", "user_id": state["user-id"], "game_id": game_id }));
    }

    return (
        <div>
            <Button onClick={createGame}>Create Game</Button>
            <div>
                Join one of the games below
            </div>
            {(!state["game-list"] || state["game-list"].length === 0) && "There seem to be no games. Why don't you create one?"}
            {state["game-list"] && state["game-list"].map((x, idx) => joinGameButton(x, `Game ${idx+1}` ,x.id, () => {joinGame(x.id)}))}
        </div>
    )
}

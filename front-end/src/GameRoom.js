import React from "react";
import Button from 'react-bootstrap/Button';


const joinGame = function(game_id, user_id, socket) {
    socket.send(JSON.stringify({type: "join_game", "user_id": user_id, "game_id": game_id }));
}



const joinGameButton = function(game, title, key, onClick, user_id){
    const nameList = game.users.map(user => {return <div key={user.id}>{user.name}</div>});
    // If the user is already in the game, we cannot join
    // This will mark the CSS and also disable clicking events
    const isJoinable = game.users.filter(user => {return user.id === user_id}).length === 0;
    
    return (
        <div className={"room-to-join " + ( isJoinable ? "joinable":"non-joinable")} key={key} onClick={isJoinable ? onClick: null}>
            {title}
            {nameList}
        </div>
    )
}


const gameRoomView = function (user_id, gameList, socket) {
    
    let ownedGameList = [];
    let joinedGameList = [];
    let otherGameList = [];
    for(const game of gameList){
        if(game.owner === user_id){
            ownedGameList.push(game);
        } else if (game.users.filter(user => {return user.id === user_id})?.length > 0) {
            joinedGameList.push(game)
        } else {
            otherGameList.push(game);
        }
    }

    return  (
    <div>
        Games you have started
        <div className="rooms-to-join">
            {ownedGameList.map((x, idx) => joinGameButton(x, `Game ${idx+1}` ,x.id, () => {joinGame(x.id, user_id, socket)}, user_id ))}
        </div>
        Games you have joined
        <div className="rooms-to-join">
            {joinedGameList.map((x, idx) => joinGameButton(x, `Game ${idx+1}` ,x.id, () => {joinGame(x.id, user_id, socket)}, user_id ))}
        </div>
        Games available to you
        <div className="rooms-to-join">
            {otherGameList.map((x, idx) => joinGameButton(x, `Game ${idx+1}` ,x.id, () => {joinGame(x.id, user_id, socket)}, user_id ))}
        </div>
    </div>
    );
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


    return (
        <div>
            <Button onClick={createGame}>Create Game</Button>

            {(!state["game-list"] || state["game-list"]?.length === 0) && "There seem to be no games. Why don't you create one?"}
            
            <div className="rooms-to-join">
                {state["game-list"] && gameRoomView(state["user-id"], state["game-list"], socket)}
            </div>
        </div>
    )
}

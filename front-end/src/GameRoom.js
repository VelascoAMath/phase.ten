import React, { useState } from "react";
import Button from 'react-bootstrap/Button';


function joinGame(game_id, user_id, socket) {
    socket.send(JSON.stringify({type: "join_game", "user_id": user_id, "game_id": game_id }));
}



function joinGameButton(game, title, key, onClick, className){
    const nameList = game.users.map(user => {return <div key={user.id}>{user.name}</div>});
    // If the user is already in the game, we cannot join
    // This will mark the CSS and also disable clicking events
    
    return (
        <div className={"room-to-join " + className} key={key} onClick={onClick}>
            {title}
            {nameList}
        </div>
    )
}


function gameRoomView(user_id, gameList, socket, selectedGame, setSelectedGame) {
    
    let hostWaitGameList = [];
    let hostStartedGameList = [];
    let joinWaitGameList = [];
    let joinStartedGameList = [];
    
    for(const game of gameList){
        game["user-in-game"] = !!(game.users.filter(user => {return user_id === user.id})?.length);

        if(game.owner === user_id){
            if(game.in_progress) {
                hostStartedGameList.push(game);
            } else {
                hostWaitGameList.push(game);
            }
        } else{
            if(game.in_progress) {
                joinStartedGameList.push(game)
            } else {
                joinWaitGameList.push(game);
            }
        }
    }

    return  (
    <div>
        <h1>Games you are hosting</h1>
        <div>
            <h2>Waiting for Players to join</h2>
            <div className="rooms-to-join">
                {hostWaitGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1} ${game['user-in-game']}`, game.id, () => {setSelectedGame(game.id)}, ("available " + (selectedGame === game.id ? "selected": ""))))}
            </div>
            <h2>Games in progress</h2>
            <div className="rooms-to-join">
                {hostStartedGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1} ${game['user-in-game']}`, game.id, () => {setSelectedGame(game.id)}, ("in-progress " + (selectedGame === game.id ? "selected": "")) ))}
            </div>
        </div>
        <h1>Games you have joined</h1>
        <div>
            <h2>Waiting for players to join</h2>
            <div className="rooms-to-join">
                {joinWaitGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1} ${game['user-in-game']}`, game.id, () => {setSelectedGame(game.id); if(!game['user-in-game']){joinGame(game.id, user_id, socket)} }, ("available " + (selectedGame === game.id ? "selected": "")) ))}
            </div>
            <h2>Games in progress</h2>
            <div className="rooms-to-join">
                {joinStartedGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1} ${game['user-in-game']}`, game.id, () => {setSelectedGame(game.id); joinGame(game.id, user_id, socket)}, ("in-progress " + (selectedGame === game.id ? "selected": "")) ))}
            </div>

        </div>
    </div>
    );
}

export default function PlayerPage({props}) {

    const{state, socket} = props;
    const [selectedGame, setSelectedGame] = useState(null);

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

    function getButtonForGameAction() {
        const user_id = state["user-id"];
        const gameList = state["game-list"];

        const game = gameList.filter((game) => {return game.id === selectedGame})[0];
        if(game.owner === user_id){
            if(game.in_progress){
                return <button>Delete Game</button>;
            } else {
                return <button>Start Game</button>;
            }
        } else {
            if(game.in_progress){
                return <button>Play Game</button>
            } else {
                return <button>Unjoin Game</button>
            }
        }
    }


    return (
        <div>
            {selectedGame &&
                getButtonForGameAction()
            }

            {(!state["game-list"] || state["game-list"]?.length === 0) && "There seem to be no games. Why don't you create one?"}
            
            <div className="rooms-to-join">
                {state["game-list"] && gameRoomView(state["user-id"], state["game-list"], socket, selectedGame, setSelectedGame)}
            </div>
            <Button onClick={createGame}>Create Game</Button>
        </div>
    )
}

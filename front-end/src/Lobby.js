import React, { useState } from "react";
import { useLocation } from "wouter";


function joinGame(game_id, user_id, socket) {
    if(socket.readyState === socket.OPEN){
        socket.send(JSON.stringify({type: "join_game", "user_id": user_id, "game_id": game_id }));
    }
}


function unjoinGame(game_id, user_id, socket) {
    if(socket.readyState === socket.OPEN){
        socket.send(JSON.stringify({type: "unjoin_game", "user_id": user_id, "game_id": game_id }));
    }
}


function startGame(game_id, user_id, socket){
    if(socket.readyState === socket.OPEN){
        socket.send(JSON.stringify({type: "start_game", "user_id": user_id, "game_id": game_id}))
    }
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
    
    let finishedGameList = [];
    let hostWaitGameList = [];
    let hostStartedGameList = [];
    let joinWaitGameList = [];
    let joinStartedGameList = [];
    
    for(const game of gameList){
        game["user-in-game"] = !!(game.users.filter(user => {return user_id === user.id})?.length);


        if(game.winner !== "None"){
            finishedGameList.push(game);
        } else if(game.host === user_id){
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
    <>
        <div className="room-section">
            <h2>Games in progress</h2>
            <div className="rooms">
                {hostStartedGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1}`, game.id, () => {setSelectedGame(game.id)}, ("in-progress " + (selectedGame === game.id ? "selected": "")) ))}
                {joinStartedGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1}`, game.id, () => {
                    if(!game["user-in-game"] && (game.in_progress === 0 || game.in_progress === false)) {
                        joinGame(game.id, user_id, socket);
                    }
                    if((game.in_progress === 1 || game.in_progress === true) && game["user-in-game"]){
                        setSelectedGame(game.id);
                    }
                },
                ("in-progress " + (selectedGame === game.id ? "selected": "")) ))}
            </div>
        </div>
        <div className="room-section">
            <h2>Waiting for players to join</h2>
            <div className="rooms">
                {hostWaitGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1}`, game.id, () => {setSelectedGame(game.id)}, ("available " + (selectedGame === game.id ? "selected": ""))))}
                {joinWaitGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1}`, game.id, () => {setSelectedGame(game.id); if(!game['user-in-game']){joinGame(game.id, user_id, socket)} }, ("available " + (selectedGame === game.id ? "selected": "")) ))}
            </div>
        </div>
        <div className="room-section">
            <h2>Finished Game</h2>
            <div className="rooms">
                {finishedGameList.map((game, idx) => joinGameButton(game, `Game ${idx+1}`, game.id, () => {setSelectedGame(game.id)}, ("in-progress " + (selectedGame === game.id ? "selected": ""))))}
            </div>
        </div>

    </>
    );
}

export default function Lobby({props}) {

    const{state, socket} = props;
    const [selectedGame, setSelectedGame] = useState(null);
    let [_, navigate] = useLocation();

    if(!(state["user-id"] && state["user-token"])){
        return (
            <div>
                You must log in first!
            </div>
        )
    }

    const createGame = function() {
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "create_game", "user_id": state["user-id"] }));
        }
    }

    function getButtonForGameAction() {
        const user_id = state["user-id"];
        const gameList = state["game-list"];
        if(gameList?.length === 0){
            return [];
        }

        const game = gameList.filter((game) => {return game.id === selectedGame})[0];
        if(game === null || game === undefined){
            setSelectedGame(null);
            return [];
        }
        const game_id = game.id;
        if(game.host === user_id){
            if(game.in_progress){
                return [
                    <button onClick={() => {navigate("/play/" + game_id)} }>Enter Game</button>,
                    <button style={{backgroundColor: "red", color: "white"}} onClick={() => {if (window.confirm("Are you sure you want to delete this game?")) {unjoinGame(game_id, user_id, socket); setSelectedGame(null)}}}>Delete Game</button>,
                ];
            } else {
                return [
                    <button onClick={() => {startGame(game_id, user_id, socket); setSelectedGame(null); navigate("/play/" + game_id) }}>Start Game</button>,
                    <button style={{backgroundColor: "red", color: "white"}} onClick={() => {if (window.confirm("Are you sure you want to delete this game?")) {unjoinGame(game_id, user_id, socket); setSelectedGame(null)}}}>Delete Game</button>,
                ];
            }
        } else {
            if(game.in_progress){
                return [<button onClick={() => navigate("/play/" + game_id)}>Play Game</button>]
            } else {
                return [<button onClick={() => {unjoinGame(game_id, user_id, socket); setSelectedGame(null)}}>Unjoin Game</button>]
            }
        }
    }

    let buttonList = [<button onClick={createGame}>Create Game</button>];
    if (selectedGame){
        buttonList.push(...getButtonForGameAction());
    }
    while(buttonList.length < 3){
        buttonList.push(<div></div>);
    }

    return (
        <div>

            {(!state["game-list"] || state["game-list"]?.length === 0) && "There seem to be no games. Why don't you create one?"}

            <div style={{display: "flex", flexDirection: "row", justifyContent: "space-between"}}>
                {buttonList}
            </div>

            <div className="rooms-to-join">
                {(state["game-list"]?.length > 0) && gameRoomView(state["user-id"], state["game-list"], socket, selectedGame, setSelectedGame)}
            </div>
        </div>
    )
}

import React, { useState } from "react";
import { useLocation } from "wouter";



const starFill = function(){
    return <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">
    <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
  </svg>;
}



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


export default function Lobby({props}) {

    const{state, socket} = props;
    const [selectedGame, setSelectedGame] = useState(null);
    let [ , navigate] = useLocation();
    const userId = state["user-id"];

    let userIdToName = {};
    if(state["user-list"]){
        for(const user of state["user-list"]){
            userIdToName[user.id] = user.name;
        }
    }


    if(!(state["user-id"] && state["user-token"])){
        return (
            <div>
                You must log in first!
            </div>
        )
    }

    const gameList = state["game-list"];

    const createGame = function() {
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "create_game", "user_id": state["user-id"] }));
        }
    }
    
    
    function tryToDelete(game_id, user_id, socket){
        if(socket.readyState === socket.OPEN){
            if(selectedGame.in_progress){
                if(window.confirm("Are you sure you want to delete this game? It's already in progress")){
                    unjoinGame(game_id, user_id, socket);
                    setSelectedGame(null);
                }
            } else {
                unjoinGame(game_id, user_id, socket);
                setSelectedGame(null);
            }
        }
    }


    return (
        <div>

            {(!gameList || gameList?.length === 0) && "There seem to be no games. Why don't you create one?"}

            <div style={{display: "flex", flexDirection: "row", justifyContent: "space-between"}}>
                <button onClick={createGame}>Create Game</button>
                {selectedGame && <button onClick={() => {tryToDelete(selectedGame.id, userId, socket)}}>Delete Game</button>}
            </div>

            <div className="rooms-to-join">
                {gameList?.map((game) => {
                    const isHost = game.host === userId;
                    const isInGame = game.users.filter((user) => {return user.id === userId}).length > 0;
                    const nonHostUsers = game.users.filter((user) => {return user.id !== game.host});
                    
                    // Game in progress which we didn't join
                    if(!isInGame && game.in_progress){
                        return null;
                    }

                    let className = "room-to-join";
                    if(game === selectedGame){
                        className += " selected";
                    }

                    return (
                        <div className={className} onClick={() => {if(game === selectedGame){setSelectedGame(null)} else {setSelectedGame(game)}}}>
                            {game.in_progress && starFill()} Host: {userIdToName[game.host]}
                            <hr/>
                            {
                                nonHostUsers.map((user) => {
                                    return <div>{user.name}</div>
                                })
                            }
                            <hr/>
                            {!isInGame && !game.in_progress && <button onClick={() => joinGame(game.id, userId, socket)}>Join</button>}
                            {isInGame && !isHost && !game.in_progress && <button onClick={() => {unjoinGame(game.id, userId, socket)}}>Unjoin</button>}
                            {isInGame && !isHost && game.in_progress && <button onClick={() => {navigate("/play/" + game.id)}}>Play</button>}
                            {isHost && !game.in_progress && nonHostUsers.length > 0 && <button onClick={() => {startGame(game.id, userId, socket)}}>Start</button>}
                            {isHost && game.in_progress && <button onClick={() => {navigate("/play/" + game.id)}}>Play</button>}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

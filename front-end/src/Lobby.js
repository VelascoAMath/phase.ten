import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation } from "wouter";
import { emojiFrownFill, starFill, trophyFill } from "./Icons";



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



// Function to sort the games
// First games displayed are those which are waiting for players
// Second games displayed are those which are in progress
// Final games shown are those which have been completed
// In each category, the games are sorted in reverse chronological order based on the last move made
function gameCompare(gameA, gameB){

    if(gameA.in_progress && gameB.in_progress){
        if(!gameA.winner && !gameB.winner){
            return gameB.updated_at.localeCompare(gameA.updated_at)
        } else if (gameA.winner && !gameB.winner){
            return 1;
        } else if (!gameA.winner && gameB.winner) {
            return -1;
        } else {
            return gameB.updated_at.localeCompare(gameA.updated_at);
        }
    } else if(gameA.in_progress && !gameB.in_progress){
        return 1;
    } else if (!gameA.in_progress && gameB.in_progress) {
        return -1;
    } else {
        return gameB.updated_at.localeCompare(gameA.updated_at)
    }
}


export default function Lobby({props}) {

    const{state, socket} = props;
    const [selectedGame, setSelectedGame] = useState(null);
    const { t } = useTranslation();

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
                {t('mustLogIn')}
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
                if(window.confirm(t("deleteGameWarning"))){
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

            {(!gameList || gameList?.length === 0) && t("noGamesMessage")}

            <div style={{display: "flex", flexDirection: "row", justifyContent: "space-between"}}>
                <button onClick={createGame}>{t('createGame')}</button>
                {selectedGame?.host === userId && <button onClick={() => {navigate("/edit_game/" + selectedGame.id)}}>{t('edit')}</button>}
                {selectedGame && <button onClick={() => {tryToDelete(selectedGame.id, userId, socket)}}>{t('deleteGame')}</button>}
            </div>

            <div className="rooms-to-join">
                {gameList
                ?.toSorted(gameCompare)
                ?.map((game) => {
                    const isHost = game.host === userId;
                    const isInGame = game.users.filter((user) => {return user.id === userId}).length > 0;
                    const nonHostUsers = game.users.filter((user) => {return user.id !== game.host});

                    // The icon to display based on the game being in progress and having a winner
                    let icon = null;
                    if(game.in_progress){
                       if(game.winner === null){
                        icon = starFill();
                       } else {
                        if(game.winner === userId){
                            icon = trophyFill();
                        } else {
                            icon = emojiFrownFill();
                        }
                       }
                    }

                    // Game in progress which we didn't join
                    if(!isInGame && game.in_progress){
                        return null;
                    }

                    let className = "room-to-join";
                    if(game === selectedGame){
                        className += " selected";
                    }

                    return (
                        <div className={className} key={game.id} onClick={() => {if(game === selectedGame){setSelectedGame(null)} else {setSelectedGame(game)}}}>
                            {icon} {t('host')}: {userIdToName[game.host]}
                            <hr/>
                            {
                                nonHostUsers.map((user) => {
                                    return <div>{user.name}</div>
                                })
                            }
                            <hr/>
                            {!isInGame && !game.in_progress && <button onClick={() => joinGame(game.id, userId, socket)}>{t('join')}</button>}
                            {isInGame && !isHost && !game.in_progress && <button onClick={() => {unjoinGame(game.id, userId, socket)}}>{t('unjoin')}</button>}
                            {isInGame && !isHost && game.in_progress && <button onClick={() => {navigate("/play/" + game.id)}}>{t('play')}</button>}
                            {isHost && !game.in_progress && nonHostUsers.length > 0 && <button onClick={() => {startGame(game.id, userId, socket)}}>{t('start')}</button>}
                            {isHost && game.in_progress && <button onClick={() => {navigate("/play/" + game.id)}}>{t('play')}</button>}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

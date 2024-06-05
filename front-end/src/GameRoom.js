import React, { useState } from "react";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';


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
        socket.send(JSON.stringify({type: "create_game", "user_id": state["user-id"] }))        
    }

    return (
        <div>
            <Button onClick={createGame}>Create Game</Button>
            <div>
                Join one of the games below
            </div>
            {state["game-list"] && state["game-list"].map(x => <button key={x.id}>Join{x.id}</button> ) }
            {(!state["game-list"] || state["game-list"].length === 0) && "There seem to be no games. Why don't you create one?"}
            {state["game-list"] && state["game-list"].map(x => <div key={x.id}>{JSON.stringify(x)}</div> ) }
        </div>
    )
}

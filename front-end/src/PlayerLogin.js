import React, { useState } from "react";

export default function PlayerLogin({props}) {


	const{state, dispatch, socket} = props;

    const getPlayers = function() {
        if(socket.readyState === 1){
            socket.send(JSON.stringify({type: "get_users"}));
        }
    }

    getPlayers();


	return (
		<div>
			<div>
				Name: {state["user-name"]}
			</div>
			<div>
				User ID: {state["user-id"]}
			</div>
			<div>
				Token: {state["user-token"]}
			</div>
			<div>
                {state["user-list"].map(user => {
                    const setUser = function(){
                        dispatch({type: "change-input", key: "user-id", value: user["id"]});
                        dispatch({type: "change-input", key: "user-name", value: user["name"]});
                        dispatch({type: "change-input", key: "user-token", value: user["token"]});
                    }
                    return <button key={user.id} onClick={setUser}>{user.name}</button>
                })}
			</div>
            <button onClick={getPlayers}>Refresh</button>
		</div>
	)
}

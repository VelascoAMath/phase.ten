import React, { useState } from "react";

export default function PlayerCreation({props}) {


	const{state, dispatch, socket} = props;

	const [name, setName] = useState("");

	const createNewPlayer = function() {
		setName("");
		socket.send(JSON.stringify({type: "new_user", name: name}));
	}

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
			<input value={name} onInput={(e) => {setName(e.target.value)}} onKeyDown={(e) => {if(e.key === "Enter") {createNewPlayer()} }}/>
			<button onClick={createNewPlayer}>Confirm Name</button>
		</div>
	)
}

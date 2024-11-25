import React, { useState } from "react";
import { useTranslation } from "react-i18next";

export default function PlayerCreation({props}) {


	const{state, socket} = props;
	const { t } = useTranslation();

	const [name, setName] = useState("");

	const createNewPlayer = function() {
		if(socket.readyState === 2 || socket.readyState === 3){
			alert("Server connection has been lost!");
			return
		}
		if(socket.readyState === socket.OPEN){
			setName("");
			socket.send(JSON.stringify({type: "new_user", name: name}));
		}
	}

	return (
		<div>
			<div>
				{t('name')}: {state["user-name"]}
			</div>
			<div>
				{t('userID')}: {state["user-id"]}
			</div>
			<div>
				{t('token')}: {state["user-token"]}
			</div>
			<input value={name} onInput={(e) => {setName(e.target.value)}} onKeyDown={(e) => {if(e.key === "Enter") {createNewPlayer()} }}/>
			<button onClick={createNewPlayer}>{t('confirmName')}</button>
		</div>
	)
}

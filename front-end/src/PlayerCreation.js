import React, { useState } from "react";
import { useLocation } from "wouter";
import { navigate } from "wouter/use-location";
import callPOST from "./callPOST";

export default function PlayerCreation() {


	const [location, setLocation] = useLocation();

	const [data, setData] = useState({
		"user_name": "",
		"display_name": "",
		"password": "",
		"confirmation_password": ""
	});
	

	const submitPlayer = async function(){
		let response = null;
		try {
			response = callPOST("http://localhost:8000/players.json", data);
			console.log(response);
		} catch (error) {
			console.log(error);
			alert("Could not create player");
			return;
		}
		if(response !== null){
			alert("Player successfully created!");
			setLocation("/");
		} else {
			alert("Could not create player!");
		}
	}

	const getInputRows = function(){
		let result = [];
		for(const [key, val] of Object.entries(data)) {
			result.push( <tr><td>{key}:</td><td><input value={val} onChange={(e) => {setData({...data, [key]: e.target.value} ) }} ></input> </td> </tr> )
		}
		return result;
	}

	return (
		<table>
			{getInputRows()}	
			<button onClick={submitPlayer}>Create new player!</button>
		</table>
	);
}

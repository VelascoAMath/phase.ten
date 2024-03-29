import React, { useEffect, useState } from "react";
import { useParams } from "wouter";

export default function PlayerPage() {
	
	const params = useParams();
	const playerId = params?.id;
	const [data, setData] = useState(null);
	const player = data?.player;
	const hand = data?.hand;

	useEffect(() => {

		const fetchPlayer = async () => {
		  try{
			  const url = "http://localhost:8000/players/" + playerId;
			  const response = await fetch(url, {
				  "headers": {
				  "Content-Type": "application/json",
				  "Accept"      : "application/json",
			  },
			  "method": "GET",
		  })
		  const json = await response.json();
		  setData(json);
		} catch(error){
			console.error(error);
		}
	}
  
		fetchPlayer();
  
	})
	
	return (
		<div>
			<h1>
			{player? player.name : ""}
			</h1>
			<div>
				{player && JSON.stringify(player)}
			</div>
			<div>
				{hand && JSON.stringify(hand)}
			</div>
		</div>
	);
}

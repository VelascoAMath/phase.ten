import React, { useEffect, useState } from "react";

export default function PlayerPage() {
	
	const playerId = 1;
	const [data, setData] = useState(null);
	const player = data?.player;

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
  
	}, [])
	
	return (
		<h1>
		  {player? player.name : ""}
		  {data && JSON.stringify(data)}
		  {player && JSON.stringify(player)}
		</h1>
	);
}

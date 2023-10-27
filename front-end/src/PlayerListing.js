import React, { useEffect, useState } from "react";

export default function PlayerListing() {

    const [players, setPlayers] = useState([]);

    useEffect(() => {

      const fetchPlayers = async () => {
        try{
            const url = "http://localhost:8000/players.json";
            const response = await fetch(url, {
                "headers": {
                "Content-Type": "application/json",
                "Accept"      : "application/json",
            },
            "method": "GET",
        })
        const json = await response.json();
        json.sort((a, b) => {return a.name.localeCompare(b.name); });
        setPlayers(json);
        } catch(error){
        console.error(error);
        }
      }

      fetchPlayers();

    }, [])

    const getPlayerDivs = function(){  
      const x = players.map((player) => {return <div key={player.id}>{player.name}</div>} );
      return x;
  }



    return (
        <div className="player-collection">
          {getPlayerDivs()}
        </div>
    );
}

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

    const deletePlayer = async (id) => {
      try{
          const url = "http://localhost:8000/players/" + id;
          const response = await fetch(url, {
              "headers": {
              "Content-Type": "application/json",
              "Accept"      : "application/json",
              "body"        : JSON.stringify({id: id})
          },
          "method": "DELETE",
      })
      const json = await response.json();
    } catch(error){
        console.error(error);
      }
    }

    const getPlayerDivs = function(){  
      const x = players.map((player) => {return <div key={player.id}>
        <button onClick={() => {
          const answer = confirm("Are you sure you want to delete " + player.name + "?");
          if(answer){
            deletePlayer(player.id);
            // window.location.reload();
          }
        }}>Delete player</button>
        {player.name}
        </div>} );
      return x;
  }



    return (
        <div className="player-collection">
          {getPlayerDivs()}
        </div>
    );
}

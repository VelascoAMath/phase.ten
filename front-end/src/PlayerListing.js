import React, { useEffect, useState } from "react";
import { Link } from "wouter";

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
          await fetch(url, {
              "headers": {
              "Content-Type": "application/json",
              "Accept"      : "application/json",
              "body"        : JSON.stringify({id: id})
          },
          "method": "DELETE",
      })
      window.location.reload();
    } catch(error){
        console.error(error);
      }
    }

    const getPlayerDivs = function(){  
      const x = players.map((player) => {return <div key={player.id}>
        <button onClick={() => {
          const answer = window.confirm("Are you sure you want to delete " + player.name + "?");
          if(answer){
            deletePlayer(player.id);
          }
        }}>Delete player</button>
        <a href={"/player/" + player.id} >{player.name}</a>
        </div>} );
      return x;
  }



    return (
      <div>
        <div className="player-collection">
          {getPlayerDivs()}
        </div>
        <div>
          <Link to="/">Home</Link>
        </div>
      </div>
    );
}

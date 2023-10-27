import React, { useState } from "react";

export default function PlayerCreation() {


    const [name, setName] = useState("");

    const submitPlayer = async function(){
        if (name === ""){
            return;
        }
        await fetch("http://localhost:8000/players.json", {
            "headers": {
                "Content-Type": "application/json",
                "Accept"      : "application/json",
            },
            "body": JSON.stringify({
                "name": name,
            }),
            "method": "POST",
        });
        window.location.reload();
    }

    return (
        <div>
            <input value={name} onChange={(e) => {setName(e.target.value)}}></input>
          <button onClick={submitPlayer}>Create new player!</button>
        </div>
    );
}

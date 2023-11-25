import React, { useState } from "react";
import { useLocation } from "wouter";
import { navigate } from "wouter/use-location";
import callPOST from "./callPOST";

export default function PlayerCreation() {


    const [location, setLocation] = useLocation();

    const [name, setName] = useState("");
    

    const submitPlayer = async function(){
        if (name === ""){
            return;
        }
        callPOST("http://localhost:8000/players.json", {
            "name": name,
        });
        alert("Player successfully created!");
        setLocation("/");
    }

    return (
        <div>
            <input value={name} onKeyDown={(e) => { if(e.code === 'Enter'){ submitPlayer() } }} onChange={(e) => {setName(e.target.value)}}></input>
          <button onClick={submitPlayer}>Create new player!</button>
        </div>
    );
}

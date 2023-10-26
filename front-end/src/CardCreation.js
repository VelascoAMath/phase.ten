import React, { useState } from "react";

export default function CardCreation() {


    const [rank, setRank] = useState(localStorage.getItem("rankToSubmit") || "ONE");
    const [color, setColor] = useState(localStorage.getItem("colorToSubmit") || "RED");

    const submitCard = async function(){
        await fetch("http://localhost:8000/cards.json", {
            "headers": {
                "Content-Type": "application/json",
                "Accept"      : "application/json",
            },
            "body": JSON.stringify({
                "rank": rank,
                "color": color
            }),
            "method": "POST",
        });
        window.location.reload();
    }
    
    const submitSkip = async function(){
        await fetch("http://localhost:8000/cards.json", {
            "headers": {
                "Content-Type": "application/json",
                "Accept"      : "application/json",
            },
            "body": JSON.stringify({
                "rank": "SKIP",
                "color": "SKIP"
            }),
            "method": "POST",
        });
        window.location.reload();
    }

    const submitWild = async function(){
        await fetch("http://localhost:8000/cards.json", {
            "headers": {
                "Content-Type": "application/json",
                "Accept"      : "application/json",
            },
            "body": JSON.stringify({
                "rank": "WILD",
                "color": "WILD"
            }),
            "method": "POST",
        });
        window.location.reload();
    }

    

    return (
        <div>
          <label>Rank</label>
          <select value={rank} onChange={(e) => {setRank(e.target.value); localStorage.setItem("rankToSubmit", e.target.value)}}>
            <option>ONE</option>
            <option>TWO</option>
            <option>THREE</option>
            <option>FOUR</option>
            <option>FIVE</option>
            <option>SIX</option>
            <option>SEVEN</option>
            <option>EIGHT</option>
            <option>NINE</option>
            <option>TEN</option>
            <option>ELEVEN</option>
            <option>TWELVE</option>
          </select>
          <label>Color</label>
          <select value={color} onChange={(e) => {setColor(e.target.value); localStorage.setItem("colorToSubmit", e.target.value)}}>
          <option>RED</option>
          <option>BLUE</option>
          <option>GREEN</option>
          <option>YELLOW</option>
          </select>
          <button onClick={submitCard}>Create Card</button>
          <button onClick={submitSkip}>Create Skip</button>
          <button onClick={submitWild}>Create Wild</button>
        </div>
    );
}

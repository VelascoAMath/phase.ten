import React, { useEffect, useState } from "react";
import useFetch from "./useFetch";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import callPOST from "./callPOST";



const socket = new WebSocket("ws://localhost:8001");

socket.onopen = (event) => {
  socket.send(JSON.stringify("Hello!"));
}



export default function GamePlay(props) {
    const [sockMessage, setSockMessage] = useState([]);

    socket.onmessage = (event) => {
        console.log("on message is being called");
        console.log(event);
        setSockMessage([...sockMessage, event.data]);
    }

    const send = function(message){
        if (socket && socket.readyState == socket.OPEN){
            socket.send(JSON.stringify(message));
        }
    }

    const getClassFromRank = function(rank) {
        if(rank === 'S'){
            return 'card S';
        }
        if(rank === 'W'){
            return 'card W';
        }
        return 'card';
    }

    
    const colorOrder = ["red", "blue", "green", "yellow", "S", "S", "W", "W"];
    const rankOrder = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "S", "W", "W"];
    const createDeck = function() {

        let result = [];

        let id = 0;
        for(const color of colorOrder){
            for(const rank of rankOrder){
                    for(let i = 0; i < 2; i++){
                    if((color === "W" || rank === "W") && color !== rank){
                        continue;
                    }
                    if((color === "S" || rank === "S") && color !== rank){
                        continue;
                    }
                    result.push({"rank": rank, "color": color === "S" ? "black" : color, "id": id++});    
                }
            }
        }

        result.sort((a, b) => {return 2 * Math.random() - 1} )

        return result;
    }

    const initialDeck = createDeck();
    const initialHand = [];
    for(const i of Array(10)){
        initialHand.push(initialDeck.pop());
    }
    const [discard, setDiscard] = useState([initialDeck.pop()]);
    const [deck, setDeck] = useState(initialDeck);
    const [hand, setHand] = useState(initialHand);
    const [playerState, setPlayerState] = useState("Drawing");
    const [cardToDiscard, setCardToDiscard] = useState(-1);
    

    const cardToDiv = function(card, onClick) {
        return <div style={{backgroundColor: card.color}} className={getClassFromRank(card.rank)} key={card.id} onClick={onClick}>{card.rank}</div>;
    }

    const getDeckDivs = function (deck, onClick) {
        return deck.map((x) => cardToDiv(x, onClick));
    }

    return (
        <div style={{display: "flex", flexDirection: "column", rowGap: "20px"}}>
            <div className="player-console">
                {getDeckDivs(discard)}
                <div className="card" style={{backgroundColor:"#004998"}}>Phase 10</div>
            </div>
            <div className="player-console">
                {playerState == "Drawing" && <Button onClick={ () => {hand.push(deck.pop()); setHand(hand); setDeck(deck); setPlayerState("Discarding")} }>Draw from the Deck</Button>}
                {playerState == "Drawing" && <Button onClick={ () => {hand.push(discard.pop()); setHand(hand); setDiscard(discard); setDeck(deck); setPlayerState("Discarding") } }>Draw from the Discard</Button>}
                {playerState == "Discarding" && <Button onClick={ () => {if(cardToDiscard == -1){return;} send("Complete Turn"); setPlayerState("Drawing"); setDiscard([...discard, hand.filter((x)=> x.id == cardToDiscard)[0] ]); setHand(hand.filter((x) => x.id != cardToDiscard)) } }>Send Message</Button>}
            </div>
            <div className="card-collection">
                {hand.map((x, idx) => <div style={{backgroundColor: x.color}} className={getClassFromRank(x.rank)} key={x.id} onClick={() => {setCardToDiscard(x.id)}}>{x.rank}</div>)}
            </div>
            <div>
                <Button onClick={() => {setHand([...hand].sort( (a, b) => {return (colorOrder.indexOf(a.color) - colorOrder.indexOf(b.color)) || (rankOrder.indexOf(a.rank) - rankOrder.indexOf(b.rank))} ))}}>Sort by Color</Button>
                <Button onClick={() => {setHand([...hand].sort( (a, b) => {return (rankOrder.indexOf(a.rank) - rankOrder.indexOf(b.rank)) || (colorOrder.indexOf(a.color) - colorOrder.indexOf(b.color))} ))}}>Sort by Rank</Button>
            </div>
            <div style={{width: "50%", overflow: "scroll", height: "50vh"}}>
                <h2>Received message</h2>
                {sockMessage.map(x => <div>{x}</div>)}
            </div>
        </div>
    )
}

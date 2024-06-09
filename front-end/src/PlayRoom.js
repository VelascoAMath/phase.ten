import { useState } from "react";
import { useParams } from "wouter";


const rankToColor = {
    "R": "red",
    "B": "blue",
    "Y": "yellow",
    "G": "green",
};

const getClassFromRank = function(rank) {
    if(rank === 'S'){
        return 'card skip';
    }
    if(rank === 'W'){
        return 'card wild';
    }
    return 'card';
}

const getDeckDivs = function(deck, selectedCards, setSelectedCards){
    
    
    
    return deck.map(
        (card, idx) => {
            let className = getClassFromRank(card.rank);
            if(selectedCards.includes(card.id)){
                className = className + " selected";
            }
            const onClick = function(card) {
                if(selectedCards.includes(card.id)){
                    setSelectedCards(selectedCards.filter((id) => {return id !== card.id}));
                } else {
                    setSelectedCards([...selectedCards, card.id]);
                }
            }
            return(
                <div style={{backgroundColor: rankToColor[card.color]}} key={idx} className={className} onClick={() => onClick(card)}>
                    {card.rank}
                </div>
            );
        }
    );
}




export default function PlayRoom({props}) {
    const{state, dispatch, socket} = props;

	const params = useParams();
	const game_id = params?.id;
    const name = state["user-name"];
    const user_id = state["user-id"];
    const game = state["game-list"]?.filter(game => game.id === game_id)[0];
    const [selectedCards, setSelectedCards] = useState([]);

    if(game === undefined){
        return <div>{game_id} is not a valid game room!</div>
    }

    // Either we haven't made a call to get the player data
    if(state["player"] === undefined){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "get_player", "user_id": user_id, "game_id": game_id }));
        }
        return <div>Getting player data {socket.readyState} {JSON.stringify(state["player"])}</div>
    }
    // Or we have old player information
    if(state["player"]["game_id"] !== game_id || state["player"]["user_id"] !== user_id){

        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "get_player", "user_id": user_id, "game_id": game_id }));
            return <div>Getting player data {JSON.stringify(state["player"])}</div>
        }
    }

    const player = state["player"]["player"];
    if(player === undefined){
        return <div>
            <div>You are not a player in this game!</div>
            <div>{game_id}</div>
            <div>{user_id}</div>
            {JSON.stringify(state)}
            </div>
    }

    const hand = player["hand"];
    const player_id = player["id"];

    const drawDeck = function(){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "draw_deck", player_id: player_id}));
        }
    }
    
    const discardSelected = function() {
        if(selectedCards.length > 1){
            alert("You can only discard one card!");
            return;
        }
        if(selectedCards.length === 0){
            alert("Selected a card to discard!");
            return;
        }
        if(socket.readyState === socket.OPEN){
            const message = JSON.stringify({type: "player_action", action: "discard", player_id: player_id, card_id: selectedCards[0]});
            socket.send(message);
            setSelectedCards([]);
        }
    }

    const sortByColor = function(){

        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "sort_by_color", player_id: player_id}));
        }
    }

    const sortByRank = function(){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "sort_by_rank", player_id: player_id}));
        }
    }





    return (
        <div>
            <div>
                User is {name} {user_id}
            </div>
            <div>
                Play room {game_id}
            </div>

            <div className="card-collection">
                {getDeckDivs(game["discard"], selectedCards, setSelectedCards) }
            </div>
            <div className="card-collection">
                {getDeckDivs(player["hand"], selectedCards, setSelectedCards )}
            </div>
            <div className="player-console">
                <button onClick={() => {sortByRank(hand)}}>Sort by rank</button>
                <button onClick={() => {sortByColor(hand)}}>Sort by color</button>
                <button onClick={drawDeck}>Draw Deck</button>
                <button onClick={discardSelected}>Discard Selected Card</button>
            </div>
            <div>{JSON.stringify(selectedCards)}</div>
            <div className="card-collection">
                {getDeckDivs(game["deck"],selectedCards, setSelectedCards)}
            </div>
        </div>
    )
}
import { useEffect, useState } from "react";
import { useLocation, useParams } from "wouter";
import { checkCircleFill, xCircleFill } from "./Icons";


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

const getDeckDivs = function(deck){

    return deck.map(
        (card, idx) => {
            let className = getClassFromRank(card.rank);
            return(
                // Implement the offsets so the cards overlap when using relative posititioning
                <div style={{backgroundColor: rankToColor[card.color], left:(-20 * idx) + "px", zIndex:(idx) }} key={idx} className={className}>
                    {card.rank}
                </div>
            );
        }
    );
}


const getDeckDivsSelectable = function(deck, selectedCards, setSelectedCards){

    return deck.map(
        (card, idx) => {
            let className = getClassFromRank(card.rank);
            if(selectedCards.includes(card)){
                className = className + " selected";
            }
            const onClick = function(card) {
                if(selectedCards.includes(card)){
                    setSelectedCards(selectedCards.filter((x) => {return x.id !== card.id}));
                } else {
                    setSelectedCards([...selectedCards, card]);
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
    const{state, socket} = props;

	const params = useParams();
    let [, navigate] = useLocation();
	const game_id = params?.id;
    const user_id = state["user-id"];
    const game = state["game"];
    const [selectedCards, setSelectedCards] = useState([]);
    const [wantToSkip, setWantToSkip] = useState(false);
    const [selectedSkipPlayer, setSelectedSkipPlayer] = useState(null);

    const [time, setTime] = useState(new Date(Date.now()));

    // Due to the numerous renders that occur at once, we need a flag to make sure that we don't have multiple functions updating the timer
    const [timeOutExists, setTimeOutExists] = useState(true);

    let last_move_made = new Date(game?.last_move_made);
    let next_player_alarm = new Date(game?.next_player_alarm);
    const secondsRemaining = Math.ceil((next_player_alarm - time) / 1000);
    const formatedTimeRemaining = Math.floor(secondsRemaining / 3600) + ":" + Math.floor((secondsRemaining % 3600) / 60).toString().padStart(2, "0") + ":" + Math.floor(secondsRemaining % 60).toString().padStart(2, "0");

    const mustWaitForOtherPlayer = next_player_alarm - time > 0;

    useEffect(() => {
        if(game){
            if(mustWaitForOtherPlayer && timeOutExists){
                setTimeOutExists(false);
                setTimeout(() => {
                    setTime(new Date(Date.now()));
                    setTimeOutExists(true);
                }, 100);
            }
        }
    }, [game, time])

    // Either we haven't made a call to get the player data
    if(state["player"] === undefined){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "get_player", "user_id": user_id, "game_id": game_id }));
        }
        return <div>Getting player data</div>
    }
    // Or we have old player information
    if(state["player"]["game_id"] !== game_id || state["player"]["user_id"] !== user_id){

        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "get_player", "user_id": user_id, "game_id": game_id }));
            return <div>Getting player data</div>
        }
    }

    if(game === undefined){
        return <div>{game_id} is not a valid game room!</div>
    }

    const player = state["player"]["player"];
    if(player === undefined){
        alert("You are not a player in this game!");
        navigate("/lobby");
        return <div></div>;
    }

    if (game["winner"] !== null){
        if(game["winner"] === user_id) {
            return <div className="winner">You have won!!!</div>
        } else {
            return <div className="winner">Sucks to be a loser</div>
        }
    }


    const hand = player["hand"];
    const player_id = player["id"];
    const discardDeck = game["discard"];

    const isCurrentPlayer = (player.user_id === game.current_player);
    const hasSkip = hand.filter(card => {return card.rank === "S"}).length > 0;

    const roomPlayers = game["players"];
    

    const drawDeck = function(){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "draw_deck", player_id: player_id}));
        }
    }

    const drawDiscard = function(){
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "draw_discard", player_id: player_id}));
        }
    }

    const discardSelected = function() {
        setSelectedCards([]);
        if(selectedCards.length > 1){
            alert("You can only discard one card!");
            return;
        }
        if(selectedCards.length === 0){
            alert("Selected a card to discard!");
            return;
        }
        if(socket.readyState === socket.OPEN){
            const message = JSON.stringify({type: "player_action", action: "discard", player_id: player_id, card_id: selectedCards[0].id});
            socket.send(message);
        }
    }

    const skipPlayer = function() {
        setSelectedSkipPlayer(null);
        setWantToSkip(false);
        setSelectedCards([]);
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "skip_player", player_id: player_id, to: selectedSkipPlayer}))
        }
    }

    const completePhase = function() {
        setSelectedCards([]);
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "complete_phase", player_id: player_id, cards: selectedCards}));
        }
    }

    const putDown = function(phase_deck_id, direction) {
        setSelectedCards([]);
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "player_action", action: "put_down", player_id: player_id, phase_deck_id: phase_deck_id, direction: direction, cards: selectedCards}));
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

    const skipSlowPlayer = function() {
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "skip_slow_player", player_id: player_id}));
        }
    }


    return (
        <div>
            <div className="phase-list">
                {game.phase_list.map((phase, idx) => <div className={"phase " + ((player.phase_index === idx) ? "selected": "")}>{phase}</div>)}
            </div>
            <div className="room-players">
                {roomPlayers.map((player) => {
                    const className = "player " + ((player.user_id === game.current_player) ? "current ": "") + ((player.skip_cards.length > 0) ? "skipped": "");
                    return (<div className={className} key={player.id}> <div>{player.display}</div>
                        <div>Phase {player.phase_index + 1}</div>
                        <div>{player.hand_size} {player.hand_size === 1 ? "card": "cards"}</div>
                        <div>{game.phase_list[player.phase_index]}</div>
                        {!player.completed_phase && <div style={{display: "flex", alignItems: "flex-end"}}> <div>Phase:</div> <div/> {xCircleFill()} </div>}
                        { !!player.completed_phase && <div style={{display: "flex", alignItems: "flex-end"}}> <div>Phase:</div> <div/> {checkCircleFill()} </div>}
                        </div>);
                    }
                )}
            </div>
            <div className="messages">
                {game.message_list.map((message) => {

                    return <div>{message.message}</div>
                })}
            </div>
            <h2 style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                You are on phase {player.phase_index + 1} - {player.phase}
            </h2>
            <h2 style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                {(player.completed_phase === 0) && "You have not completed your phase"}
                {(player.completed_phase === 1) && "You have completed your phase"}
            </h2>
            <div>
                Play room {game_id}
            </div>

            <div style={{alignItems: "center", gap: "10px 10px", flexWrap: "nowrap", justifyContent: "space-between", margin: "auto", maxWidth: "750px" }} className="card-collection">
                <div style={{display: "flex"}}>
                    {isCurrentPlayer && (!player["drew_card"]) && (discardDeck.length > 0) && (discardDeck[discardDeck.length - 1].rank !== "S") && <button onClick={drawDiscard}>Draw Discard</button>}
                    {getDeckDivs(discardDeck.slice(discardDeck.length-1)) }

                </div>
                <div style={{display: "flex"}}>
                    <div className="card">Deck</div>
                    {isCurrentPlayer && (!player["drew_card"]) && <button onClick={drawDeck}>Draw Deck</button>}
                </div>
            </div>
            <div>
                <div>
                    {mustWaitForOtherPlayer && formatedTimeRemaining}
                    {mustWaitForOtherPlayer && <div>Waiting</div>}
                </div>
                {!mustWaitForOtherPlayer && !isCurrentPlayer && <button onClick={skipSlowPlayer}>Skip {game.players.filter((p) => {return p.user_id === game.current_player})[0].display} for wasting our time</button>}
                {!mustWaitForOtherPlayer && isCurrentPlayer && <div>You're in danger of getting skipped!!!</div>}
            </div>
            
            <div style={{marginTop: "10px"}} className="card-collection">
                {getDeckDivsSelectable(player["hand"], selectedCards, setSelectedCards )}
            </div>
            <div className="player-console">
                <button onClick={() => {sortByRank(hand)}}>Sort by rank</button>
                <button onClick={() => {sortByColor(hand)}}>Sort by color</button>
            </div>
            {(player["drew_card"]) && <div className="player-console">
                <button onClick={discardSelected}>Discard Selected Card</button>
            </div>}
            {isCurrentPlayer && (!player["drew_card"]) && <div className="player-console">
            </div>}
            {(player["drew_card"]) && isCurrentPlayer && hasSkip && <div className="player-console">
                {wantToSkip && <button onClick={() => {setWantToSkip(false); setSelectedSkipPlayer(null)}}>Don't Skip Player</button>}
                {!wantToSkip && <button onClick={() => setWantToSkip(true)}>Skip Player</button>}
            </div>}
            {
                (player["drew_card"]) && wantToSkip &&
                <div style={{display: "flex", flexDirection: "column", alignItems: "center", border: "5px white solid"}}>
                    <h3>Who do you want to skip?</h3>
                    <div>
                        {game.users.filter(user => user.id !== player.user_id).map(user => <button key={user.id} style={{border: (user.id === selectedSkipPlayer ? "solid red 2px": "")}} onClick={() => setSelectedSkipPlayer(user.id)}>{user.display}</button> )}
                    </div>
                    {selectedSkipPlayer && <button onClick={skipPlayer}>Skip Player</button>}
                </div>
            }
            <div style={{display: "flex", flexDirection: "column", justifyContent: "center"}}>
                <h2 style={{marginLeft: "auto", marginRight: "auto"}}>Selected card(s)</h2>
                <div className="card-collection">
                    {getDeckDivsSelectable(selectedCards, selectedCards, setSelectedCards)}
                </div>
                {isCurrentPlayer && (selectedCards.length > 0) && player["drew_card"] && !player.completed_phase && <button onClick={completePhase}>Complete Phase</button>}
            </div>
            <div>
                {game["phase_decks"].toSorted((a, b) => {return a.id.localeCompare(b.id)}).map((deck) => {
                    return (
                        <div className="phase-deck-collection" key={deck.id}>
                            <button style={{width: "150px"}} onClick={() => {putDown(deck.id, "start")}}>Put down at start</button>
                            <h2>{deck.phase}:</h2> <div className="card-collection">{getDeckDivs(deck["deck"])} </div>
                            <button style={{width: "150px"}} onClick={() => {putDown(deck.id, "end")}}>Put down at end</button>
                        </div>
                        ); })}
            </div>
        </div>
    )
}
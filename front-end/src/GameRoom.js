import React, { useEffect, useState } from "react";
import useFetch from "./useFetch";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import callPOST from "./callPOST";


export default function PlayerPage() {

    const fetchGame = function () {
        fetch("http://localhost:8000/games/", {
            "headers": {
            "Content-Type": "application/json",
            "Accept"      : "application/json",
        },
        "method": "GET",
        })
        .then(res => {
        if (!res.ok) { // error coming back from server
            throw Error('could not fetch the data for that resource');
        } 
        return res.json();
        })
        .then(data => {
            console.log(data);
         setGames([...data]);
        })
        .catch(err => {
        // auto catches network / connection error
        alert(err.message);
        })
    }
	
    const [games, setGames] = useState([]);
    console.log(games);

    useEffect(() => {
        fetchGame();
    }, [])


    return (
        <div>
            <InputGroup className="mb-3">
                <Form.Control
                placeholder="Join a game"
                aria-label="Join a game"
                aria-describedby="basic-addon2"
                />
                <Button variant="outline-secondary" id="button-addon2">
                    Join Game
                </Button>
            </InputGroup>
            <Button onClick={ () => {const _ = callPOST("http://localhost:8000/games/"); fetchGame()}}>Create Game</Button>
            <div>
                Games
            </div>
            { games && games.map(x => JSON.stringify(x) )}
            {!games && "There seem to be no games. Why don't you create one?"}
        </div>
    )
}

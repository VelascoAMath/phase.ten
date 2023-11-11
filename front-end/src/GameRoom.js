import React from "react";
import useFetch from "./useFetch";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import callPOST from "./callPOST";


export default function PlayerPage() {
	
    const [games, isPending, error] = useFetch("http://localhost:8000/games/");
    console.log(games);


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
            <Button onClick={() => {callPOST("http://localhost:8000/games/")}}>Create Game</Button>
            <div>
                Games
            </div>
            {isPending && "Loading"}
            {!isPending &&  games && games.map(x => JSON.stringify(x) )}
            {!isPending && !games && "There seem to be no games. Why don't you create one?"}
        </div>
    )
}

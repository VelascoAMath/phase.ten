import { useEffect, useState } from "react";
import { useLocation, useParams } from "wouter";


export default function EditGame({props}) {
    const{state, dispatch, socket} = props;
    const params = useParams();
    let [, navigate] = useLocation();
    const game_id = params?.id;
    const user_id = state["user-id"];
    const game = state["game-list"].filter((g) => g.id == game_id)[0];

    const [phaseInput, setPhaseInput] = useState(game?.phase_list);

    useEffect(() => {
        setPhaseInput(game?.phase_list);
    }, [game])

    if(!game){
        return <div>{game_id} is not a valid game id!</div>
    }

    return (
        <div>
            <h1>Edit game {game.id}</h1>
            <h2>Phase List</h2>
            {phaseInput?.map((phase, idx) => {
                return <input key={idx} value={phase} onChange={(e) => {let phaseInputCopy = [...phaseInput]; phaseInputCopy[idx] = e.target.value.toLocaleUpperCase(); setPhaseInput(phaseInputCopy)}}/>
            })}
            <div>
                <button onClick={() => {setPhaseInput([...phaseInput, ""])}} >Add Phase</button>
                <button onClick={() => {setPhaseInput(phaseInput.filter((_, idx) => {return idx < phaseInput.length - 1}))}} >Remove Phase</button>
                <button onClick={() => {if(socket.readyState === socket.OPEN){socket.send(JSON.stringify({type: "edit_game_phase", "user_id": user_id, "game_id": game_id, new_phase: phaseInput }))} }}>Change Phase</button>
                <button onClick={() => {if(socket.readyState === socket.OPEN){socket.send(JSON.stringify({type: "edit_game_phase", "user_id": user_id, "game_id": game_id, new_phase: ["S3+S3","S3+R4","S4+R4","R7","R8","R9","S4+S4","C7","S5+S2","S5+S3"] }))} }} >Reset</button>
            </div>

            <h2>Game Type</h2>
            {game.type}
            <h2>Players</h2>
            <ul>
                {game.users.map((user) => <li key={user.id}>{user.name} {user.id === game.current_player && "(Current player)"}  {user.id === game.winner && "(Winner)"} </li>)}
            </ul>
            <h2>Created At</h2>
            {game.created_at}
            <h2>Updated At</h2>
            {game.updated_at}
        </div>
    )
}
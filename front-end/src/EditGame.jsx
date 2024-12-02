import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "wouter";


export default function EditGame({props}) {
    const{state, socket} = props;
    const params = useParams();

    const { t } = useTranslation();

    const game_id = params?.id;
    const user_id = state["user-id"];
    const game = state["game-list"].filter((g) => g.id === game_id)[0];

    const [phaseInput, setPhaseInput] = useState(game?.phase_list);

    useEffect(() => {
        setPhaseInput(game?.phase_list);
    }, [game])

    if(!game){
        return <div>{t('invalidGameId', {gameID: game_id})}</div>
    }

    return (
        <div>
            <h1>{t('editGame')} {game.id}</h1>
            <h2>{t('phaseList')}</h2>
            {phaseInput?.map((phase, idx) => {
                return <input key={idx} value={phase} onChange={(e) => {let phaseInputCopy = [...phaseInput]; phaseInputCopy[idx] = e.target.value.toLocaleUpperCase(); setPhaseInput(phaseInputCopy)}}/>
            })}
            <div>
                <button onClick={() => {setPhaseInput([...phaseInput, ""])}} >{t('addPhase')}</button>
                <button onClick={() => {setPhaseInput(phaseInput.filter((_, idx) => {return idx < phaseInput.length - 1}))}} >{t('removePhase')}</button>
                <button onClick={() => {if(socket.readyState === socket.OPEN){socket.send(JSON.stringify({type: "edit_game_phase", "user_id": user_id, "game_id": game_id, new_phase: phaseInput }))} }}>{t('changePhase')}</button>
                <button onClick={() => {if(socket.readyState === socket.OPEN){socket.send(JSON.stringify({type: "edit_game_phase", "user_id": user_id, "game_id": game_id, new_phase: ["S3+S3","S3+R4","S4+R4","R7","R8","R9","S4+S4","C7","S5+S2","S5+S3"] }))} }} >{t('reset')}</button>
            </div>

            <h2>{t('gameType')}</h2>
            {game.type}
            <h2>{t('players')}</h2>
            <ul>
                {game.users.map((user) => <li key={user.id}>{user.name} {user.id === game.current_player && "(" + t('currentPlayer') + ")"}  {user.id === game.winner && "(" + t('winner') + ")"} </li>)}
                <button onClick={() => {socket.send(JSON.stringify({type: "add_bot", "user_id": user_id, "game_id": game_id }))}}>{t('addBot')}</button>
            </ul>
            <h2>{t('createdAt')}</h2>
            {game.created_at}
            <h2>{t('updatedAt')}</h2>
            {game.updated_at}
        </div>
    )
}
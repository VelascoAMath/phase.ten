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

    const [timeLimit, setTimeLimit] = useState({days: 0, hours: game?.player_time_limit[0] || 0, minutes: game?.player_time_limit[1] || 0, seconds: 0});
    const timeUnitList = ["days", "hours", "minutes", "seconds"];

    if(timeLimit.seconds >= 60){
        setTimeLimit({...timeLimit, seconds: timeLimit.seconds - 60, minutes: timeLimit.minutes + 1});
    }
    if(timeLimit.minutes >= 60){
        setTimeLimit({...timeLimit, minutes: timeLimit.minutes - 60, hours: timeLimit.hours + 1});
    }
    if(timeLimit.hours >= 24){
        setTimeLimit({...timeLimit, hours: timeLimit.hours - 24, days: timeLimit.days + 1});
    }

    if(timeLimit.seconds < 0){
        setTimeLimit({...timeLimit, minutes: timeLimit.minutes - 1, seconds: timeLimit.seconds + 60});
    }
    if(timeLimit.minutes < 0){
        setTimeLimit({...timeLimit, hours: timeLimit.hours - 1, minutes: timeLimit.minutes + 60});
    }
    if(timeLimit.hours < 0){
        setTimeLimit({...timeLimit, days: timeLimit.days - 1, hours: timeLimit.hours + 24});
    }
    if(timeLimit.days < 0){
        setTimeLimit({days: 0, hours: 0, minutes: 0, seconds: 0});
    }

    useEffect(() => {
        setPhaseInput(game?.phase_list);
        setTimeLimit({days: game?.player_time_limit[0], hours: Math.floor(game?.player_time_limit[1]/ 60) || 0, minutes: game?.player_time_limit[1] % 60 || 0, seconds: 0});
    }, [game])

    if(!game){
        return <div>{t('invalidGameId', {gameID: game_id})}</div>
    }

    return (
        <div>
            <h1>{t('editGame')} {game.id}</h1>
            <h2>{t('phaseList')}</h2>
            {phaseInput?.map((phase, idx) => {
                return <input key={idx} value={phase} onChange={(e) => {if(game.in_progress){return} let phaseInputCopy = [...phaseInput]; phaseInputCopy[idx] = e.target.value.toLocaleUpperCase(); setPhaseInput(phaseInputCopy)}}/>
            })}
            {!game.in_progress && <div>
                <button onClick={() => {setPhaseInput([...phaseInput, ""])}} >{t('addPhase')}</button>
                <button onClick={() => {setPhaseInput(phaseInput.filter((_, idx) => {return idx < phaseInput.length - 1}))}} >{t('removePhase')}</button>
                <button onClick={() => {if(socket.readyState === socket.OPEN){socket.send(JSON.stringify({type: "edit_game_phase", "user_id": user_id, "game_id": game_id, new_phase: phaseInput }))} }}>{t('changePhase')}</button>
                <button onClick={() => {if(socket.readyState === socket.OPEN){socket.send(JSON.stringify({type: "edit_game_phase", "user_id": user_id, "game_id": game_id, new_phase: ["S3+S3","S3+R4","S4+R4","R7","R8","R9","S4+S4","C7","S5+S2","S5+S3"] }))} }} >{t('reset')}</button>
            </div>}

            <h2>{t('gameType')}</h2>
            {game.type}
            <h2>{t('playerTimeLimit')}</h2>
            <div className="left-to-right">
                {timeUnitList.map(timeUnit => {
                    const onChange = (e) => {
                        setTimeLimit({...timeLimit, [timeUnit]: Number(e.target.value)});
                    }

                    return <div>
                        <div className="timerTitle">{t(timeUnit)}</div>
                        <input value={timeLimit[timeUnit]} onChange={onChange} type="number"/>
                    </div>

                })}
            </div>
            <h2>{t('players')}</h2>
            <ul>
                {game.users.map((user) => <li key={user.id}>{user.name} {user.id === game.current_player && "(" + t('currentPlayer') + ")"}  {user.id === game.winner && "(" + t('winner') + ")"} </li>)}
                <button onClick={() => {socket.send(JSON.stringify({type: "add_bot", "user_id": user_id, "game_id": game_id }))}}>{t('addBot')}</button>
                <button onClick={() => {socket.send(JSON.stringify({type: "remove_bot", "user_id": user_id, "game_id": game_id }))}}>{t('removeBot')}</button>
            </ul>
            <h2>{t('createdAt')}</h2>
            {game.created_at}
            <h2>{t('updatedAt')}</h2>
            {game.updated_at}
        </div>
    )
}
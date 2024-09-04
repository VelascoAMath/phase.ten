import { useLocation, useParams } from "wouter";





export default function EditGame({props}) {
    const{state, dispatch, socket} = props;
	const params = useParams();
    let [, navigate] = useLocation();
	const game_id = params?.id;
    const user_id = state["user-id"];
    const game = state["game-list"].filter((g) => g.id == game_id)[0];

    if(!game){
        return <div>{game_id} is not a valid game id!</div>
    }


    return (
        <div>
            <h1>Edit game {game.id}</h1>
            <h2>Phase List</h2>
            {JSON.stringify(game.phase_list)}
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
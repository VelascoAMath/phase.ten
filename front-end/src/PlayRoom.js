import { useParams } from "wouter";




export default function PlayRoom({props}) {
    const{state, dispatch, socket} = props;

	const params = useParams();
	const game_id = params?.id;


    return (
        <div>
            Play room {game_id}
            <div>
                {JSON.stringify(state["game-list"])}
            </div>
        </div>
    )
}
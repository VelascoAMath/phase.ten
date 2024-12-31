import React from "react";
import { useTranslation } from "react-i18next";

export default function PlayerLogin({props}) {


	const{state, dispatch, socket} = props;

	const { t } = useTranslation();

    const getPlayers = function() {
        if(socket.readyState === socket.OPEN){
            socket.send(JSON.stringify({type: "get_users"}));
        }
    }


	return (
		<div>
			<div>
				{t('name')}: {state["user-name"]}
			</div>
			<div>
				{t('display')}: {state["user-display"]}
			</div>
			<div>
				{t('userID')}: {state["user-id"]}
			</div>
			<div>
				{t('token')}: {state["user-token"]}
			</div>
			<div>
                {state["user-list"]?.filter(user => !user.is_bot)?.map(user => {
                    const setUser = function(){
                        dispatch({type: "change-input", key: "user-id", value: user["id"]});
                        dispatch({type: "change-input", key: "user-name", value: user["name"]});
                        dispatch({type: "change-input", key: "user-display", value: user["display"]});
                        dispatch({type: "change-input", key: "user-token", value: user["token"]});
                    }
                    return <button key={user.id} onClick={setUser}>{user.name}</button>
                })}
			</div>
            <button onClick={getPlayers}>{t('refresh')}</button>
            <button onClick={() => {dispatch({type: "change-input", key: "user-id", value: null}); dispatch({type: "change-input", key: "user-name", value: null}); dispatch({type: "change-input", key: "user-token", value: null});} }>{t('logOut')}</button>
		</div>
	)
}

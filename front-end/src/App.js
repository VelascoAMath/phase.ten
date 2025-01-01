import './App.css';
import React, { useReducer, useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';

import Home from './Home.js';

import Lobby from './Lobby';
import { Route, useLocation } from "wouter";
import inputReducer from './InputReducer.js';
import PlayerLogin from './PlayerLogin.js';
import PlayRoom from './PlayRoom.js';
import PlayerCreation from './PlayerCreation.js';
import EditGame from './EditGame.jsx';

import alarmSound from "./turn_alarm.wav";
import { globe } from './Icons.js';
import { SOCKET_URL } from './URL.jsx';

const initState = {
  "user-id": localStorage.getItem("user-id"),
  "user-name": localStorage.getItem("user-name"),
  "user-display": localStorage.getItem("user-display"),
  "user-token": localStorage.getItem("user-token"),
  "socket": new WebSocket(SOCKET_URL),
  "game-list": [],
};

// List of languages
const lngs = {
  en: { nativeName: 'English' },
  es: { nativeName: 'Español' }
};


function App() {

  const [state, dispatch] = useReducer(inputReducer, initState);
  const [socketState, setSocketState] = useState(0);
  const [initialSocketCall, setInitialSocketCall] = useState(false);
  const [canPlayDing, setCanPlayDing] = useState(false);
  const { t, i18n } = useTranslation();
  let [ , navigate] = useLocation();


  const ding = new Audio(alarmSound);

  const socket = state["socket"];

  socket.onerror = (event) => {
    setSocketState(-1);
  }

  socket.onopen = (event) => {
    if(socket.readyState === socket.OPEN){
      if(!initialSocketCall){
        socket.send(JSON.stringify({type: "connection"}));
        socket.send(JSON.stringify({type: "get_games"}));
        socket.send(JSON.stringify({type: "get_users"}));
        setInitialSocketCall(true);
      }
      setSocketState(1);
    }
  }

  socket.onclose = (event) => {
    if(socket.readyState === socket.OPEN){
      socket.send(JSON.stringify({type: "disconnection"}));
    }
    setSocketState(-1);

  }


  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
    if(data["type"] === "new_user"){
      dispatch({type: "change-input", key: "user-id", value: data.user["id"]});
      dispatch({type: "change-input", key: "user-name", value: data.user["name"]});
      dispatch({type: "change-input", key: "user-display", value: data.user["display"]});
      dispatch({type: "change-input", key: "user-token", value: data.user["token"]});
      localStorage.setItem("user-id", data.user["user-id"]);
      localStorage.setItem("user-name", data.user["user-name"]);
      localStorage.setItem("user-display", data.user["user-display"]);
      localStorage.setItem("user-token", data.user["user-token"]);
    }
    else if(data["type"] === "get_users"){
      dispatch({type: "change-input", key: "user-list", value: data["users"].toSorted((a, b) => a.name.localeCompare(b.name)) })
      let validToken = false;
      // Validate our stored session data
      for(const user of data["users"]){
        if(user.id === state["user-id"] && user.name === state["user-name"] && user.token === state["user-token"]){
          validToken = true;
          break;
        }
      }
      // We have old data and it needs to be deleted
      if(!validToken){
        localStorage.removeItem("user-id");
        localStorage.removeItem("user-name");
        localStorage.removeItem("user-display");
        localStorage.removeItem("user-token");
        dispatch({type: "change-input", key: "user-id", value: null});
        dispatch({type: "change-input", key: "user-name", value: null});
        dispatch({type: "change-input", key: "user-display", value: null});
        dispatch({type: "change-input", key: "user-token", value: null});
      }
    } else if (data["type"] === "get_games"){
      dispatch({type: "change-input", key: "game-list", value: data["games"]})
    } else if(data["type"] === "create_game"){
      dispatch({type: "change-input", key: "game-list", value: [...state["game-list"], data["game"]] })
    } else if (data["type"] === "get_player"){
      dispatch({type: "change-input", key: "player", value: data })
    } else if (data["type"] === "get_game"){
      dispatch({type: "change-input", key: "game", value: data["game"]})
    } else if(data["type"] === "rejection"){
      alert(data["message"]);
    } else if(data["type"] === "next_player" && state["user-id"] === data["user_id"]){
      if(canPlayDing){
        ding.play();
      }
    }
  }

  if(socketState === 0) {
    return <div>Establishing connection</div>
  } else if (socketState === -1){
    return (
      <>
        <div>{t('noConnection')}</div>
        <button onClick={() => {window.location.reload()}}>{t('retryConnection')}</button>
      </>
    );
  }

  return (
    <div>
      <div style={{display: "flex", justifyContent: "space-between"}}>
        <h2>{state["user-name"]}</h2>
        <div className='clickable' onClick={() => {navigate("/settings/")}}>{globe()}</div>
      </div>
      {!canPlayDing && <button onClick={() => {setCanPlayDing(true)}}>{t('notifications')}</button>}

      {/* <div>
                {state["user-list"]?.map(user => {
                  const setUser = function(){
                    dispatch({type: "change-input", key: "user-id", value: user["id"]});
                    dispatch({type: "change-input", key: "user-name", value: user["name"]});
                    dispatch({type: "change-input", key: "user-token", value: user["token"]});
                    }
                    return <button key={user.id} onClick={setUser}>{user.name}</button>
                    })}
			</div> */}
      <Route path="/signup">
        <PlayerCreation props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/settings">
        <div>
            {Object.keys(lngs).map((lng) => (
              <button key={lng} style={{ fontWeight: i18n.resolvedLanguage === lng ? 'bold' : 'normal' }} type="submit" onClick={() => i18n.changeLanguage(lng)}>
                {lngs[lng].nativeName}
                </button>
              ))}
        </div>
      </Route>
      <Route path="/login">
        <PlayerLogin props={{state, dispatch, socket}}/>
      </Route>
      {/* <Route path="/player/:id" component={PlayerPage} ></Route> */}
      {/* <Route path="/test_game">
        <GamePlay socket={socket}/>
      </Route> */}
      <Route path="/lobby">
        <Lobby props={{state, dispatch, socket}}></Lobby>
      </Route>
      <Route path="/edit_game/:id">
        <EditGame props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/play/:id">
        <PlayRoom props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/" >
        <Home props={{state, dispatch, socket}}/>
      </Route>
    </div>

  );
}

export default App;

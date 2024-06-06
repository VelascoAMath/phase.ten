import './App.css';
import React, { useReducer, useState } from 'react';
import CardCreation from './CardCreation';
import CardListing from './CardListing.js';
import Home from './Home.js';

import PlayerListing from './PlayerListing';
import PlayerCreation from './PlayerCreation'
import PlayerPage from './PlayerPage';
import GameRoom from './GameRoom';
import { Route } from "wouter";
import inputReducer from './InputReducer.js';
import PlayerLogin from './PlayerLogin.js';
import PlayRoom from './PlayRoom.js';


const initState = {
  "user-id": localStorage.getItem("user-id"),
  "user-name": localStorage.getItem("user-name"),
  "user-token": localStorage.getItem("user-token"),
};

function App() {

  const [state, dispatch] = useReducer(inputReducer, initState);
  const [socketState, setSocketState] = useState(0);
  const [initialSocketCall, setInitialSocketCall] = useState(false);
  
  const socket = new WebSocket("ws://localhost:8001");

  socket.onerror = (event) => {
    setSocketState(-1);
  }

  socket.onopen = (event) => {
    if(socket.readyState === socket.OPEN){
      if(!initialSocketCall){
        socket.send(JSON.stringify({type: "connection"}));
        socket.send(JSON.stringify({type: "get_games"}));
        setInitialSocketCall(true);
      }
      setSocketState(1);
    }
  }
    

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
    if(data["type"] === "new_user"){
      dispatch({type: "change-input", key: "user-id", value: data.user["id"]});
      dispatch({type: "change-input", key: "user-name", value: data.user["name"]});
      dispatch({type: "change-input", key: "user-token", value: data.user["token"]});
      localStorage.setItem("user-id", data.user["user-id"]);
      localStorage.setItem("user-name", data.user["user-name"]);
      localStorage.setItem("user-token", data.user["user-token"]);
    }
    else if(data["type"] === "get_users"){
      dispatch({type: "change-input", key: "user-list", value: data["users"].toSorted((a, b) => a.name.localeCompare(b.name)) })
    } else if (data["type"] === "get_games"){
      dispatch({type: "change-input", key: "game-list", value: data["games"]})
    } else if(data["type"] === "create_game"){
      dispatch({type: "change-input", key: "game-list", value: [...state["game-list"], data["game"]] })
    } else if(data["type"] === "rejection"){
      alert(data["message"]);
    }
  }
  
  if(socketState === 0) {
    return <div>Establishing connection</div>
  } else if (socketState === -1){
    return <div>Failed to establish connection</div>
  }

  return (
    <div>
      <Route path="/cards">
        <CardCreation/>
        <CardListing/>
      </Route>
      <Route path="/signup">
        <PlayerCreation props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/login">
        <PlayerLogin props={{state, dispatch, socket}}/>
      </Route>
      <Route path="/player/:id" component={PlayerPage} ></Route>
      <Route path="/players">
        <PlayerListing></PlayerListing>
      </Route>
      {/* <Route path="/test_game">
        <GamePlay socket={socket}/>
      </Route> */}
      <Route path="/games">
        <GameRoom props={{state, dispatch, socket}}></GameRoom>
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

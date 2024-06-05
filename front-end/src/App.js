import React, { useReducer } from 'react';
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

function App() {

  const [state, dispatch] = useReducer(inputReducer, {});
  
  const socket = new WebSocket("ws://localhost:8001");

  socket.onopen = (event) => {
    socket.send(JSON.stringify({type: "connection"}));
  }
    

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
    if(data["type"] === "new_user"){
      dispatch({type: "change-input", key: "user-id", value: data.user["id"]});
      dispatch({type: "change-input", key: "user-name", value: data.user["name"]});
      dispatch({type: "change-input", key: "user-token", value: data.user["token"]});
    }
    else if(data["type"] === "get_users"){
      dispatch({type: "change-input", key: "user-list", value: data["users"].toSorted((a, b) => a.name.localeCompare(b.name)) })
    } else if (data["type"] === "get_games"){
      dispatch({type: "change-input", key: "game-list", value: data["games"]})
    }
    else if(data["type"] === "rejection"){
      alert(data["message"]);
    }
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
      <Route path="/" >
        <Home props={{state, dispatch, socket}}/>
      </Route>
    </div>

  );
}

export default App;

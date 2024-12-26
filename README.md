


You will need two terminals to run this game


## Terminal 1

Create a file called URL.jsx and defined an exported constant called SOCKET_URL which is a string pointing to the network address of the server's websocket.
This is an example of how the file should look.

export const SOCKET_URL = "ws://127.0.0.1:8001";



> cd front-end
> npm install --legacy-peer-deps
> npm start



## Terminal 2

> cd socket
> python app.py




In front-end/src/App.js the websocket is intially configured to connect to localhost
If you wish to play this game on a local network, you will need to replace that with the local ip address of the server


You will need Python3.12 to run this game without modifications
You wil also need to download several libraries using pip
If you cannot run app.py, look at the error messages to see what you need to install



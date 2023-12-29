import React from 'react';
import { Link } from 'wouter';


export default function Hello() {
	


	return (
		<h1>
			<div>
				<Link to="/signup">Sign Up</Link>
			</div>
			<div>
				<Link to="/login">Log In</Link>
			</div>
			<div>
				<Link to="/players">Look at players</Link>
			</div>
			<div>
				<Link to="/cards">Look at cards</Link>
			</div>
			<div>
				<Link to="/games">Play a game</Link>
			</div>
			<div>
				<Link to="/test_game">Test out our websockets</Link>
			</div>
		</h1>
	)
}

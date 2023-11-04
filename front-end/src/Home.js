import React from 'react';
import { Link } from 'wouter';


export default function Hello() {
	


	return (
		<h1>
			<div>
				<Link to="/players">Look at players</Link>
			</div>
			<div>
				<Link to="/cards">Look at cards</Link>
			</div>
		</h1>
	)
}

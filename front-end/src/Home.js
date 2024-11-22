import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'wouter';


export default function Home({props}) {
	
	const { t } = useTranslation();
	
	return (
		<h1>
			<div>
				<Link to="/signup">{t('signUp')}</Link>
			</div>
			<div>
				<Link to="/login">{t('login')}</Link>
			</div>
			{/* <div>
				<Link to="/players">Look at players</Link>
			</div>
			<div>
				<Link to="/cards">Look at cards</Link>
			</div> */}
			<div>
				<Link to="/lobby">{t('playGame')}</Link>
			</div>
			{/* <div>
				<Link to="/test_game">Test out our websockets</Link>
			</div> */}
		</h1>
	)
}

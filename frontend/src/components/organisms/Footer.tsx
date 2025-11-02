import React from 'react';

export function Footer() {
	return (
		<footer className="mt-12 border-t border-white/10 pt-6 text-sm text-white/60">
			<div className="flex flex-col sm:flex-row items-center justify-between gap-3">
				<div>© {new Date().getFullYear()} Super Litera</div>
				<nav className="flex items-center gap-4">
					<a className="hover:text-white" href="#">Privacy</a>
					<a className="hover:text-white" href="#">Terms</a>
					<a className="hover:text-white" href="#">Contact</a>
				</nav>
			</div>
		</footer>
	);
}

export default Footer;



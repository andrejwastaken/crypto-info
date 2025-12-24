import { useState } from "react";

const Footer = () => {
	const [isSubmitted, setIsSubmitted] = useState(false);

	const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setIsSubmitted(true);
		setTimeout(() => setIsSubmitted(false), 1000);
	};

	return (
		<footer className="bg-amber-100">
			<div className="flex flex-col items-center py-8 gap-4">
				<div className="text-center">
					<h3 className="text-lg font-semibold text-slate-900 mb-2">
						Follow the latest trends
					</h3>
					<p className="text-sm text-slate-800 mb-4">
						With our daily newsletter
					</p>
					<form onSubmit={handleSubmit} className="flex gap-2 max-w-md">
						<input
							type="email"
							placeholder="you@example.com"
							required
							className="flex-1 px-4 py-2 border border-amber-300 rounded focus:outline-none focus:ring-2 focus:ring-amber-300 bg-white"
						/>
						<button
							type="submit"
							disabled={isSubmitted}
							className="px-6 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 transition-colors cursor-pointer disabled:bg-slate-600 disabled:cursor-not-allowed"
						>
							{isSubmitted ? "Submitted" : "Submit"}
						</button>
					</form>
				</div>
			</div>
			<div className="bg-amber-100 text-center py-4">
				<p className="text-sm text-slate-900">
					CryptoInfo © All rights reserved
				</p>
			</div>
		</footer>
	);
};

export default Footer;

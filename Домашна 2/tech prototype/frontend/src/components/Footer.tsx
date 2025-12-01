const Footer = () => {
	return (
		<footer className="bg-transparent">
			<div className="flex flex-col items-center py-8 gap-4">
				<div className="text-center">
					<h3 className="text-lg font-semibold text-gray-800 mb-2">
						Follow the latest trends
					</h3>
					<p className="text-sm text-gray-600 mb-4">
						With our daily newsletter
					</p>
					<div className="flex gap-2 max-w-md">
						<input
							type="email"
							placeholder="you@example.com"
							className="flex-1 px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-gray-400"
						/>
						<button className="px-6 py-2 bg-gray-800 text-white rounded hover:bg-gray-700 transition-colors">
							Submit
						</button>
					</div>
				</div>
			</div>
			<div className="bg-gray-300 text-center py-4">
				<p className="text-sm text-gray-700">
					CryptoInfo © All rights reserved
				</p>
			</div>
		</footer>
	);
};

export default Footer;

const AboutPage = () => {
	return (
		<div className="container mx-auto px-4 py-8 max-w-4xl">
			<section className="mb-8">
				<h2 className="text-2xl font-bold mb-4">Goal:</h2>
				<p className="text-lg text-gray-800 leading-relaxed">
					CryptoInfo is an application that allows users to access, visualize,
					and analyze historical data for the top 1,000 active cryptocurrencies.
					The primary focus is placed on the collection and processing of daily
					data spanning at least the last 10 years (or the maximum available
					period for each currency), thereby creating a foundation for technical
					analysis and the tracking of market trends.
				</p>
			</section>

			<section className="mb-8">
				<h2 className="text-2xl font-bold mb-4">Team members:</h2>
				<div className="text-lg text-gray-800">
					<p>Dimitar Arsov - 231017</p>
					<p>Filip Gavrilovski - 231136</p>
					<p>Andrej Ristikj - 231133</p>
				</div>
			</section>

			<section className="mb-8">
				<h2 className="text-2xl font-bold mb-4">Contact:</h2>
				<div className="flex items-center gap-4 border border-gray-300 rounded-lg p-4 bg-white">
					<svg
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						strokeWidth="2"
						strokeLinecap="round"
						strokeLinejoin="round"
					>
						<rect x="2" y="4" width="20" height="16" rx="2" />
						<path d="M22 6L12 13L2 6" />
					</svg>
					<span className="text-lg">Email: cryptoinfo@gmail.com</span>
				</div>
			</section>
		</div>
	);
};

export default AboutPage;

import LinkWrapper from "../components/LinkWrapper";

const AboutPage = () => {
	return (
		<div className="container mx-auto px-4 py-8 max-w-5xl">
			<h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
				About
			</h1>

			<div className="space-y-12">
				<section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
					<h2 className="text-2xl font-semibold text-gray-800 mb-6 border-b pb-3">
						Goal
					</h2>
					<p className="text-gray-600 leading-relaxed mb-3">
						CryptoInfo is a comprehensive cryptocurrency analysis platform that
						allows users to access, visualize, and analyze historical data for
						the top 1,000 active cryptocurrencies. The primary focus is placed
						on the collection and processing of daily data spanning at least the
						last 10 years (or the maximum available period for each currency),
						thereby creating a foundation for technical analysis and the
						tracking of market trends.
					</p>
					<p className="text-gray-600 leading-relaxed mb-3">
						The platform combines multiple data sources and analytical
						approaches to provide a detailed view of the cryptocurrency market:
					</p>
					<ul className="list-disc list-inside text-gray-600 space-y-2 mb-3">
						<li>
							<strong>AI-Powered Predictions:</strong> Using LSTM neural
							networks to forecast next-day price movements based on historical
							patterns.
						</li>
						<li>
							<strong>On-Chain Analytics:</strong> Real-time blockchain metrics
							such as active addresses, transaction volumes, exchange flows, and
							DeFi TVL.
						</li>
						<li>
							<strong>Technical Analysis:</strong> Comprehensive scoring system
							combining oscillators and moving averages across multiple
							timeframes.
						</li>
						<li>
							<strong>Sentiment Analysis:</strong> NLP-powered analysis of news
							articles from major sources.
						</li>
						<li>
							<strong>Interactive Visualizations:</strong> Historical price
							charts with line and candlestick views for detailed market
							analysis.
						</li>
					</ul>
					<p className="text-gray-600 leading-relaxed">
						By integrating machine learning, blockchain data, technical
						indicators, and sentiment analysis, CryptoInfo aims to provide
						traders and investors with the tools they need to make informed
						decisions in the dynamic cryptocurrency market.
					</p>
				</section>

				<section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
					<h2 className="text-2xl font-semibold text-gray-800 mb-6 border-b pb-3">
						Team Members
					</h2>
					<div className="text-gray-600 space-y-2">
						<p>Dimitar Arsov - 231017</p>
						<p>Filip Gavrilovski - 231136</p>
						<p>Andrej Ristikj - 231133</p>
					</div>
				</section>

				<section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
					<h2 className="text-2xl font-semibold text-gray-800 mb-6 border-b pb-3">
						Source Code
					</h2>
					<p className="text-gray-600 leading-relaxed mb-4">
						This project is open source and available on{" "}
						<LinkWrapper
							text="GitHub"
							link="https://github.com/gavro081/crypto-info"
						/>
						and{" "}
						<LinkWrapper
							text="GitLab"
							link="https://gitlab.finki.ukim.mk/231136/crypto-info"
							endWithBlankSpace={false}
						/>
						.
					</p>
				</section>

				<section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
					<h2 className="text-2xl font-semibold text-gray-800 mb-6 border-b pb-3">
						Contact
					</h2>
					<p className="text-gray-600">Email: cryptoinfo@gmail.com</p>
					{/* <div className="flex items-center gap-4 border border-gray-300 rounded-lg p-4 bg-gray-50"> */}
					{/* <span className="text-gray-600">Email: cryptoinfo@gmail.com</span> */}
					{/* </div> */}
				</section>
			</div>
		</div>
	);
};

export default AboutPage;

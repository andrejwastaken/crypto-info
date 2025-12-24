import LinkWrapper from "../components/LinkWrapper";

const HowItWorksPage = () => {
	return (
		<div className="min-h-screen bg-slate-800">
			<div className="container mx-auto px-4 py-8 max-w-5xl">
				<h1 className="text-4xl font-bold text-amber-100 mb-8 text-center">
					How It Works
				</h1>

				<div className="space-y-12">
					{/* Landing Page Section */}
					<section className="bg-amber-100 rounded-lg border border-amber-400 shadow-sm p-6">
						<h2 className="text-2xl font-semibold text-slate-800 mb-6 border-b border-amber-300 pb-3">
							Landing Page Features
						</h2>

						{/* AI Predictions */}
						<div className="mb-8">
							<h3 className="text-xl font-semibold text-slate-700 mb-3 flex items-center gap-2">
								AI Predictions (Top/Bottom 5)
							</h3>
							<p className="text-slate-700 leading-relaxed mb-3">
								Our AI prediction system uses{" "}
								<LinkWrapper
									text="Long Short-Term Memory (LSTM)"
									link="https://en.wikipedia.org/wiki/Long_short-term_memory"
								/>
								neural networks to forecast cryptocurrency price movements for
								the next day. The model is trained on historical price data,
								including open, high, low, close, and volume information. It is
								evaluated using{" "}
								<LinkWrapper
									text="RMSE"
									link="https://en.wikipedia.org/wiki/Root_mean_square_deviation"
									endWithBlankSpace={false}
								/>
								,{" "}
								<LinkWrapper
									text="MAPE"
									link="https://en.wikipedia.org/wiki/Mean_absolute_percentage_error"
								/>
								and{" "}
								<LinkWrapper
									text="R squared"
									link="https://en.wikipedia.org/wiki/Coefficient_of_determination"
								/>
								metrics. The models with performance metrics under certain
								thresholds are dropped and there are no predictions provided for
								those currencies.
							</p>
							<p className="text-slate-700 leading-relaxed mb-3">
								The system analyzes patterns in the data to identify the top 5
								cryptocurrencies with the highest predicted positive change and
								the bottom 5 with the highest predicted negative change. These
								predictions are updated daily and displayed on the landing page
								to help users identify potential opportunities.
							</p>
							<p className="text-slate-600 leading-relaxed italic text-sm">
								Note: Past performance is not indicative of future results.
								Always do your own research before making investment decisions.
							</p>
						</div>

						{/* On-Chain Metrics */}
						<div className="mb-8">
							<h3 className="text-xl font-semibold text-slate-700 mb-3 flex items-center gap-2">
								On-Chain Metrics
							</h3>
							<p className="text-slate-700 leading-relaxed mb-3">
								<LinkWrapper
									text="On-Chain metrics"
									link="https://www.coinbase.com/learn/advanced-trading/what-is-onchain-analysis-and-how-to-use-it-as-a-crypto-trader"
								/>
								provide real-time insights into blockchain activity and network
								health. These metrics are collected directly from blockchain
								data and exchange APIs to give you a comprehensive view of each
								cryptocurrency's fundamental strength.
							</p>
							<div className="bg-amber-50 rounded p-4 mb-3 border border-amber-200">
								<h4 className="font-semibold text-slate-700 mb-2">
									Key Metrics Explained:
								</h4>
								<ul className="space-y-2 text-slate-700 text-sm">
									<li>
										<strong>Active Addresses:</strong> Number of unique
										addresses participating in transactions, indicating network
										activity
									</li>
									<li>
										<strong>Transactions:</strong> Total number of transactions
										on the network
									</li>
									<li>
										<strong>Exchange Inflow/Outflow:</strong> Movement of tokens
										to/from exchanges, potentially indicating buying/selling
										pressure
									</li>
									<li>
										<strong>Net Flow:</strong> Difference between inflow and
										outflow, showing overall exchange movement direction
									</li>
									<li>
										<strong>Whale Transactions:</strong> Large transactions that
										may indicate institutional activity
									</li>
									<li>
										<strong>NVT Ratio:</strong> Network Value to Transactions
										ratio, similar to P/E ratio in stocks
									</li>
									<li>
										<strong>MVRV Ratio:</strong> Market Value to Realized Value,
										indicating if an asset is over/undervalued
									</li>
									<li>
										<strong>TVL (Total Value Locked):</strong> Total value
										locked in DeFi protocols for that cryptocurrency
									</li>
									<li>
										<strong>Hash Rate:</strong> Value that represents the
										efficiency and performance of a mining machine.
									</li>
								</ul>
							</div>
							<p className="text-slate-700 leading-relaxed">
								These metrics are aggregated from multiple blockchain explorers
								and data providers, processed, and updated regularly to ensure
								accuracy.
							</p>
						</div>

						<div>
							<h3 className="text-xl font-semibold text-slate-700 mb-3 flex items-center gap-2">
								Cryptocurrency List
							</h3>
							<p className="text-slate-700 leading-relaxed mb-3">
								The main cryptocurrency table displays comprehensive market data
								for hundreds of cryptocurrencies. Data is sourced from the{" "}
								<LinkWrapper
									text="Yahoo Finance website"
									link="https://finance.yahoo.com/markets/crypto/all/"
								/>
								and is updated every day.
							</p>
							<p className="text-slate-700 leading-relaxed">
								The table includes sortable columns for market capitalization,
								trading volume, circulating supply, and 52-week price changes.
							</p>
						</div>
					</section>

					<section className="bg-amber-100 rounded-lg border border-amber-400 shadow-sm p-6">
						<h2 className="text-2xl font-semibold text-slate-800 mb-6 border-b border-amber-300 pb-3">
							Coin Detail Page Features
						</h2>

						{/* Technical Analysis */}
						<div className="mb-8">
							<h3 className="text-xl font-semibold text-slate-700 mb-3 flex items-center gap-2">
								Technical Analysis
							</h3>
							<p className="text-slate-700 leading-relaxed mb-3">
								Our technical analysis system combines multiple indicators to
								provide a comprehensive signal score ranging from -1 (Strong
								Sell) to +1 (Strong Buy). The analysis is available in three
								timeframes: daily, weekly and monthly.
							</p>
							<div className="bg-amber-50 rounded p-4 mb-3 border border-amber-200">
								<h4 className="font-semibold text-slate-700 mb-2">
									Oscillators:
								</h4>
								<ul className="space-y-2 text-slate-700 text-sm mb-4">
									<li>
										<strong>
											<LinkWrapper
												text="RSI (Relative Strength Index)"
												link="https://en.wikipedia.org/wiki/Relative_strength_index"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										indicator measuring momentum and identifying overbought or
										oversold conditions.
									</li>
									<li>
										<strong>
											<LinkWrapper
												text="Stochastic Oscillator"
												link="https://en.wikipedia.org/wiki/Stochastic_oscillator"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										indicator identifying momentum by comparing closing prices
										to price ranges.
									</li>
									<li>
										<strong>
											<LinkWrapper
												text="CCI (Commodity Channel Index)"
												link="https://en.wikipedia.org/wiki/Commodity_channel_index"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										indicator measuring price deviation from statistical mean.
									</li>
									<li>
										<strong>
											<LinkWrapper
												text="MACD (Moving Average Convergence Divergence)"
												link="https://en.wikipedia.org/wiki/MACD"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										indicator showing trend direction and momentum through the
										relationship between two moving averages.
									</li>
									<li>
										<strong>
											<LinkWrapper
												text="ADX/DMI (Directional Movement Index)"
												link="https://en.wikipedia.org/wiki/Average_directional_movement_index"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										indicator comparing positive and negative directional
										movement to identify trend strength and direction.
									</li>
								</ul>
								<h4 className="font-semibold text-slate-700 mb-2">
									Moving Averages:
								</h4>
								<ul className="space-y-2 text-slate-700 text-sm">
									<li>
										<strong>
											<LinkWrapper
												text="SMA (Simple Moving Average)"
												link="https://en.wikipedia.org/wiki/Moving_average#Simple_moving_average"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										simple average of closing prices to identify overall trend
										direction.
									</li>
									<li>
										<strong>
											<LinkWrapper
												text="EMA (Exponential Moving Average)"
												link="https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										weighted average giving more importance to recent prices for
										faster trend signals.
									</li>
									<li>
										<strong>
											<LinkWrapper
												text="WMA (Weighted Moving Average)"
												link="https://en.wikipedia.org/wiki/Moving_average#Weighted_moving_average"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										linearly weighted average placing emphasis on recent data.
									</li>
									<li>
										<strong>
											<LinkWrapper
												text="Bollinger Bands"
												link="https://en.wikipedia.org/wiki/Bollinger_Bands"
												endWithBlankSpace={false}
											/>
											:
										</strong>{" "}
										moving average with 2 standard deviation bands to measure
										volatility and identify potential support/resistance levels.
									</li>
								</ul>
								<p className="text-slate-700 text-sm mt-3">
									<strong>
										<LinkWrapper
											text="Volume Analysis"
											link="https://en.wikipedia.org/wiki/Volume_analysis"
											endWithBlankSpace={false}
										/>
										:
									</strong>{" "}
									trading volume is compared to its 20-period moving average to
									boost or dampen the final score, confirming price movements
									with volume trends.
								</p>
							</div>
							<p className="text-slate-700 leading-relaxed">
								Metrics are calculated using the Python libraries{" "}
								<LinkWrapper text="ta" link="https://pypi.org/project/ta/" />
								and{" "}
								<LinkWrapper
									text="pandas-ta"
									link="https://pypi.org/project/pandas-ta/"
									endWithBlankSpace={false}
								/>
								. Each indicator generates a signal (buy, sell, or hold), and
								these are weighted and combined to produce the final score
								displayed on the gauge. When you switch between timeframes the
								system shows the proper score for that particular timeframe.
							</p>
						</div>
						<div className="mb-8">
							<h3 className="text-xl font-semibold text-slate-700 mb-3 flex items-center gap-2">
								Price Predictions
							</h3>
							<p className="text-slate-700 leading-relaxed mb-3">
								Individual coin price predictions use the same LSTM model as the
								landing page predictions. For each cryptocurrency, the model
								analyzes its historical price patterns, trading volume, and
								market trends to forecast the closing price for the next trading
								day.
							</p>
							<p className="text-slate-700 leading-relaxed italic text-sm">
								Note: The model is retrained periodically with new data to
								improve accuracy, but all predictions should be used as one of
								many tools in your analysis, not as the sole basis for trading
								decisions.
							</p>
						</div>

						<div className="mb-8">
							<h3 className="text-xl font-semibold text-slate-700 mb-3 flex items-center gap-2">
								Historical Data & Charts
							</h3>
							<p className="text-slate-700 leading-relaxed mb-3">
								Historical price data is scraped from the{" "}
								<LinkWrapper
									text="Yahoo Finance API"
									link="https://developer.yahoo.com/api/"
								/>
								using the{" "}
								<LinkWrapper
									text="yfinance library"
									link="https://github.com/ranaroussi/yfinance"
									endWithBlankSpace={false}
								/>
								. We collect{" "}
								<LinkWrapper
									text="OHLCV data"
									link="https://www.coinapi.io/blog/understanding-ohlcv-in-market-data-analysis"
								/>
								(Open, High, Low, Close, Volume) for each currency on a daily
								basis and use it to populate the charts. This data is processed
								through a{" "}
								<LinkWrapper
									text="Pipe & Filter architecture"
									link="https://learn.microsoft.com/en-us/azure/architecture/patterns/pipes-and-filters"
								/>{" "}
								that ensures smooth operation, eliminates duplicates, and fills
								in any missing values.
							</p>
							<p className="text-slate-700 leading-relaxed mb-3">
								Two chart types are available:
							</p>
							<ul className="list-disc list-inside text-slate-700 mb-3 space-y-1">
								<li>
									<strong>Line Chart:</strong> Shows the closing price trend
									over time, ideal for quick visualization of price movements
								</li>
								<li>
									<strong>Candlestick Chart:</strong> Displays open, high, low,
									and close prices, providing more detailed information about
									price action.
								</li>
							</ul>
							<p className="text-slate-700 leading-relaxed">
								You can select different timeframes to analyze short-term
								volatility or long-term trends.
							</p>
						</div>

						<div>
							<h3 className="text-xl font-semibold text-slate-700 mb-3 flex items-center gap-2">
								News & Sentiment Analysis
							</h3>
							<p className="text-slate-700 leading-relaxed mb-3">
								News articles related to each cryptocurrency are aggregated from{" "}
								<LinkWrapper
									text="Yahoo Finance News"
									link="https://finance.yahoo.com/topic/crypto/"
								/>
								and{" "}
								<LinkWrapper
									text="Binance News"
									link="https://www.binance.com/en/square/news/all"
								/>{" "}
								web scrapers continuously monitor these sources for relevant
								content.
							</p>
							<p className="text-slate-700 leading-relaxed mb-3">
								Each article undergoes sentiment analysis using{" "}
								<LinkWrapper
									text="natural language processing (NLP)"
									link="https://en.wikipedia.org/wiki/Natural_language_processing"
								/>
								to determine whether the content is positive, negative, or
								neutral regarding the cryptocurrency. More specifically, we use
								the{" "}
								<LinkWrapper
									text="FinBERT model"
									link="https://github.com/ProsusAI/finBERT"
								/>
								that is trained specifically for tasks in the finance domain to
								ensure the sentiments are as accurate as possible. This helps
								you quickly gauge market sentiment and understand the context
								behind price movements.
							</p>
							<p className="text-slate-700 leading-relaxed">
								Articles are ranked by relevance and recency, ensuring you see
								the most important and recent news first. The sentiment score is
								displayed alongside each article to provide additional context.
							</p>
						</div>
					</section>
					{/* 
				<section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
					<h2 className="text-2xl font-semibold text-gray-800 mb-6 border-b pb-3">
						Data Collection & Updates
					</h2>

					<div className="mb-6">
						<h3 className="text-xl font-semibold text-gray-700 mb-3 flex items-center gap-2">
							How We Collect Data
						</h3>
						<p className="text-gray-600 leading-relaxed mb-3">
							Our platform uses a combination of APIs and web scrapers to
							collect data from various sources:
						</p>
						<ul className="list-disc list-inside text-gray-600 space-y-2 mb-3">
							<li>
								<strong>Price Data:</strong> Real-time and historical price data
								from major cryptocurrency exchanges via their public APIs
							</li>
							<li>
								<strong>On-Chain Data:</strong> Blockchain explorers and
								analytics platforms provide on-chain metrics
							</li>
							<li>
								<strong>News:</strong> Custom web scrapers monitor
								cryptocurrency news websites and financial news sources
							</li>
							<li>
								<strong>Market Data:</strong> Trading volume, market cap, and
								supply information from CoinMarketCap and similar aggregators
							</li>
						</ul>
					</div>

					<div>
						<h3 className="text-xl font-semibold text-gray-700 mb-3 flex items-center gap-2">
							<span className="text-green-600">⏱️</span>
							Update Frequency
						</h3>
						<p className="text-gray-600 leading-relaxed mb-3">
							Different data types are updated at different intervals:
						</p>
						<ul className="list-disc list-inside text-gray-600 space-y-1">
							<li>
								Price data: Updated every few minutes during trading hours
							</li>
							<li>On-chain metrics: Updated hourly</li>
							<li>
								Technical analysis: Recalculated on-demand when you view a coin
							</li>
							<li>AI predictions: Updated daily (typically overnight)</li>
							<li>
								News articles: Continuously scraped and added as they're
								published
							</li>
						</ul>
					</div>
				</section> */}

					<section className="bg-amber-200 border-l-4 border-amber-500 p-6 rounded">
						<h3 className="text-lg font-semibold text-slate-800 mb-2">
							Important Disclaimer
						</h3>
						<p className="text-slate-700 text-sm leading-relaxed">
							This platform provides informational and educational content only.
							None of the information provided should be considered financial
							advice or a recommendation to buy, sell, or hold any
							cryptocurrency. Always conduct your own research and consult with
							a qualified financial advisor before making investment decisions.
							Cryptocurrency investments carry significant risks, and you should
							never invest more than you can afford to lose.
						</p>
					</section>
				</div>
			</div>
		</div>
	);
};

export default HowItWorksPage;

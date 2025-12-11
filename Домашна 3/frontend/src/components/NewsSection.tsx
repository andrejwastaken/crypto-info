import { formatDistanceToNow, parseISO } from "date-fns";

export interface NewsArticle {
	title: string;
	img_src: string;
	symbols: string[];
	link: string;
	date: string;
	sentiment: "Positive" | "Negative" | "Neutral";
}

const MOCK_NEWS: NewsArticle[] = [
	{
		title: "GameStop’s $500m Bitcoin bet takes games retailer on wild ride",
		img_src: "/logo.png",
		symbols: ["COIN-USD", "BTC-USD"],
		link: "https://finance.yahoo.com/news/gamestop-500m-bitcoin-bet-takes-112435594.html",
		date: "2025-12-10 21:22:48.151169",
		sentiment: "Positive",
	},
	{
		title:
			"Donald Trump Crypto Video Game Is Almost Here — Can It Revive His Dying Memecoin?",
		img_src: "/logo.png",
		symbols: ["RANDOM-USD"],
		link: "https://finance.yahoo.com/news/donald-trump-crypto-video-game-113010329.html",
		date: "2025-12-10 16:22:48.148658",
		sentiment: "Neutral",
	},
	{
		title:
			"Crypto Markets Today: Fed Rate-Cut Hopes Lift BTC, ETH as Traders Brace for Volatility",
		img_src: "/logo.png",
		symbols: ["BTC-USD", "ETH-USD"],
		link: "https://finance.yahoo.com/news/crypto-markets-today-fed-rate-113037363.html",
		date: "2025-12-09 13:29:48.146113",
		sentiment: "Positive",
	},
	{
		title: "How Bitcoin Could Help You Retire a Millionaire",
		img_src: "/logo.png",
		symbols: ["BTC-USD"],
		link: "https://finance.yahoo.com/news/bitcoin-could-help-retire-millionaire-113500287.html",
		date: "2025-12-10 21:22:48.143716",
		sentiment: "Positive",
	},
	{
		title:
			"Metaplanet Stock Jumps 12% as mNAV Climbs to 1.17, Highest Level Since Crypto Crisis",
		img_src: "/logo.png",
		symbols: ["BTC-USD"],
		link: "https://finance.yahoo.com/news/metaplanet-stock-jumps-12-mnav-114111853.html",
		date: "2025-12-10 21:22:48.141098",
		sentiment: "Positive",
	},
	{
		title:
			"Crypto News Today, December 10 – ETH USD Back Over $3.3K as Solana Eco Coins Like Pippin and HumidiFi Surge Hard",
		img_src: "/logo.png",
		symbols: ["BTC-USD", "SOL-USD"],
		link: "https://finance.yahoo.com/news/crypto-news-today-december-10-115431345.html",
		date: "2025-10-30 21:22:48.138569",
		sentiment: "Negative",
	},
];

const getSentimentConfig = (sentiment: string) => {
	switch (sentiment) {
		case "Positive":
			return {
				colors: "bg-emerald-200 text-emerald-800 border-emerald-200",
				icon: (
					<svg
						className="w-3 h-3"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth="3"
							d="M5 10l7-7m0 0l7 7m-7-7v18"
						/>
					</svg>
				),
			};
		case "Negative":
			return {
				colors: "bg-rose-200 text-rose-800 border-rose-200",
				icon: (
					<svg
						className="w-3 h-3"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth="3"
							d="M19 14l-7 7m0 0l-7-7m7 7V3"
						/>
					</svg>
				),
			};
		default:
			return {
				colors: "bg-gray-100 text-gray-700 border-gray-200",
				icon: (
					<svg
						className="w-3 h-3"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth="3"
							d="M20 12H4"
						/>
					</svg>
				),
			};
	}
};

const formatDate = (dateString: string) => {
	const isoString = dateString.replace(" ", "T");
	const date = parseISO(isoString);
	return formatDistanceToNow(date, { addSuffix: true });
};

const NewsSection = () => {
	return (
		<div className="mt-8">
			<h2 className="text-2xl font-semibold text-gray-800 mb-4">Latest News</h2>
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{MOCK_NEWS.map((article, index) => {
					const { colors, icon } = getSentimentConfig(article.sentiment);

					return (
						<a
							key={index}
							href={article.link}
							target="_blank"
							rel="noopener noreferrer"
							className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden flex flex-col h-full"
						>
							<div className="relative h-48 overflow-hidden bg-gray-50 flex items-center justify-center">
								<img
									src={article.img_src}
									alt={article.title}
									className="object-contain h-32 w-32 transition-transform duration-500 group-hover:scale-105"
								/>

								<div
									className={`absolute top-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold shadow-sm border ${colors}`}
								>
									{icon}
									<span>{article.sentiment}</span>
								</div>
							</div>

							<div className="p-5 flex flex-col flex-1">
								<div className="flex flex-wrap gap-2 mb-3">
									{article.symbols.map((symbol) => (
										<span
											key={symbol}
											className="text-[10px] font-bold uppercase tracking-wide bg-gray-100 text-gray-500 px-2 py-1 rounded"
										>
											{symbol}
										</span>
									))}
								</div>

								<h3 className="text-base font-semibold text-gray-900 mb-3 line-clamp-3 leading-snug group-hover:text-blue-600 transition-colors">
									{article.title}
								</h3>

								<div className="mt-auto pt-4 border-t border-gray-100 flex items-center justify-between">
									<span className="text-xs text-gray-400">
										{formatDate(article.date)}
									</span>

									<div className="group/tooltip relative flex items-center gap-1 text-xs text-gray-300 hover:text-gray-500 transition-colors">
										<span className="sr-only">How do we calculate this?</span>
										<svg
											className="w-4 h-4"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												strokeLinecap="round"
												strokeLinejoin="round"
												strokeWidth="2"
												d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
											/>
										</svg>
										{/* todo: change page name */}
										<span className="hidden group-hover/tooltip:block absolute bottom-full right-0 mb-2 w-48 p-2 bg-gray-800 text-white rounded text-[10px] z-10 shadow-lg">
											The sentiment is calculated with sentiment analysis using
											the finBERT model. For more details, go to the `XXXXX`
											page.
										</span>
									</div>
								</div>
							</div>
						</a>
					);
				})}
			</div>
		</div>
	);
};

export default NewsSection;

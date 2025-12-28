import { formatDistanceToNow, parseISO } from "date-fns";
import { useEffect, useState } from "react";
import { useNewsUpdate } from "../context/NewsUpdateContext";

export interface NewsArticle {
	id: number;
	title: string;
	img_src: string;
	symbols: string[];
	link: string;
	date: string;
	sentiment: "Positive" | "Negative" | "Neutral";
	score: number;
}

interface PageInfo {
	size: number;
	totalElements: number;
	totalPages: number;
	number: number;
}

interface PagedResponse {
	_embedded: {
		textSentimentList: Array<{
			id: number;
			title: string;
			date: string;
			symbols: string[];
			link: string;
			imageLink: string;
			label: string;
			score: number;
		}>;
	};
	_links: {
		next?: {
			href: string;
		};
	};
	page: PageInfo;
}

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

// map backend sentiment labels to frontend format
const mapSentiment = (label: string): "Positive" | "Negative" | "Neutral" => {
	const lowerLabel = label.toLowerCase();
	if (lowerLabel.includes("positive")) return "Positive";
	if (lowerLabel.includes("negative")) return "Negative";
	return "Neutral";
};

interface NewsSectionProps {
	symbol?: string;
}

const NewsSection = ({ symbol }: NewsSectionProps) => {
	const [news, setNews] = useState<NewsArticle[]>([]);
	const [loading, setLoading] = useState(true);
	const [nextPageUrl, setNextPageUrl] = useState<string | null>(null);
	const [loadingMore, setLoadingMore] = useState(false);

	const { isUpdateAvailable, updateButtonText, triggerUpdate } =
		useNewsUpdate();

	const fetchNews = async () => {
		if (!symbol) return;

		setLoading(true);
		try {
			const response = await fetch(
				`http://localhost:8080/api/sentiment?symbol=${symbol.toUpperCase()}&size=9`
			);
			if (response.ok) {
				const data: PagedResponse = await response.json();
				const articles: NewsArticle[] = data._embedded.textSentimentList.map(
					(item) => ({
						id: item.id,
						title: item.title,
						img_src: item.imageLink || "/logo.png",
						symbols: item.symbols,
						link: item.link,
						date: item.date,
						sentiment: mapSentiment(item.label),
						score: item.score,
					})
				);
				setNews(articles);
				setNextPageUrl(data._links.next?.href || null);
			}
		} catch (error) {
			console.error("Failed to fetch news:", error);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchNews();
	}, [symbol]);

	// Listen for update completion event to refresh news
	useEffect(() => {
		const handleUpdateComplete = () => {
			if (symbol) {
				fetchNews();
			}
		};

		window.addEventListener("newsUpdateCompleted", handleUpdateComplete);
		return () => {
			window.removeEventListener("newsUpdateCompleted", handleUpdateComplete);
		};
	}, [symbol]);

	const handleLoadMore = async () => {
		if (!nextPageUrl || loadingMore) return;

		setLoadingMore(true);
		try {
			const response = await fetch(nextPageUrl);
			if (response.ok) {
				const data: PagedResponse = await response.json();
				const newArticles: NewsArticle[] = data._embedded.textSentimentList.map(
					(item) => ({
						id: item.id,
						title: item.title,
						img_src: item.imageLink || "/logo.png",
						symbols: item.symbols,
						link: item.link,
						date: item.date,
						sentiment: mapSentiment(item.label),
						score: item.score,
					})
				);
				setNews((prevNews) => [...prevNews, ...newArticles]);
				setNextPageUrl(data._links.next?.href || null);
			}
		} catch (error) {
			console.error("Failed to load more news:", error);
		} finally {
			setLoadingMore(false);
		}
	};

	if (!symbol) {
		return null;
	}

	if (loading) {
		return (
			<div className="mt-8">
				<h2 className="text-2xl font-semibold text-amber-100 mb-4">
					Latest News
				</h2>
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{[...Array(6)].map((_, i) => (
						<div
							key={i}
							className="bg-amber-100 rounded-xl border border-amber-400 shadow-sm overflow-hidden animate-pulse"
						>
							<div className="h-48 bg-amber-200" />
							<div className="p-5 space-y-3">
								<div className="h-4 bg-amber-200 rounded w-3/4" />
								<div className="h-4 bg-amber-200 rounded w-full" />
								<div className="h-4 bg-amber-200 rounded w-5/6" />
							</div>
						</div>
					))}
				</div>
			</div>
		);
	}

	if (news.length === 0) {
		return (
			<div className="mt-8">
				<h2 className="text-2xl font-semibold text-amber-100 mb-4">
					Latest News
				</h2>
				<p className="text-amber-200">
					No news available for this cryptocurrency.
				</p>
			</div>
		);
	}

	return (
		<div className="mt-8">
			<div className="flex flex-row items-center mb-4 justify-between">
				<h2 className="text-2xl font-semibold text-amber-100">Latest News</h2>

				<button
					onClick={triggerUpdate}
					disabled={!isUpdateAvailable}
					className={`px-6 py-2 text-sm font-medium rounded-md border transition-colors ${
						!isUpdateAvailable
							? "bg-amber-200 text-slate-800 border-amber-400 cursor-not-allowed"
							: "bg-amber-200 text-slate-800 border-amber-400 hover:bg-amber-300 hover:border-amber-500 hover:cursor-pointer"
					}`}
				>
					{updateButtonText}
				</button>
			</div>
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{news.map((article) => {
					const { colors, icon } = getSentimentConfig(article.sentiment);

					return (
						<div
							key={article.id}
							className="bg-amber-100 rounded-xl border border-amber-400 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden flex flex-col h-full"
						>
							<div className="relative h-48 overflow-hidden bg-amber-50 flex items-center justify-center">
								<img
									src={article.img_src}
									alt={article.title}
									onError={(e) => {
										e.currentTarget.src = "/logo.png";
									}}
									className="object-cover w-full h-full"
								/>

								<div
									className={`group/sentiment absolute top-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold shadow-sm border ${colors} cursor-default`}
								>
									{icon}
									<span className="group-hover/sentiment:hidden">
										{article.sentiment}
									</span>
									<span className="hidden group-hover/sentiment:inline">
										Score: {article.score.toFixed(2)}
									</span>
								</div>
							</div>

							<div className="p-5 flex flex-col flex-1">
								<div className="flex flex-wrap gap-2 mb-3">
									{article.symbols.map((symbol) => (
										<span
											key={symbol}
											className="text-[10px] font-bold uppercase tracking-wide bg-amber-200 text-slate-700 px-2 py-1 rounded"
										>
											{symbol}
										</span>
									))}
								</div>

								<a
									href={article.link}
									target="_blank"
									rel="noopener noreferrer"
									className="text-base font-semibold text-slate-900 mb-3 line-clamp-3 leading-snug hover:text-amber-700 transition-colors block"
								>
									{article.title}
								</a>

								<div className="mt-auto pt-4 border-t border-amber-200 flex items-center justify-between">
									<span className="text-xs text-slate-500">
										{formatDate(article.date)}
									</span>

									<div className="group/tooltip relative flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 transition-colors">
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
										<span className="hidden group-hover/tooltip:block absolute bottom-full right-0 mb-2 w-48 p-2 bg-gray-800 text-white rounded text-[10px] z-10 shadow-lg">
											The sentiment is calculated with sentiment analysis using
											the FinBERT model. For more details, visit the{" "}
											<span className="font-bold">How it works?</span> page.
										</span>
									</div>
								</div>
							</div>
						</div>
					);
				})}
			</div>

			{nextPageUrl && (
				<div className="flex justify-center mt-8">
					<button
						onClick={handleLoadMore}
						disabled={loadingMore}
						className={`px-6 py-2 text-sm font-medium rounded-md border transition-colors ${
							loadingMore
								? "bg-amber-200 text-slate-500 border-amber-400 cursor-not-allowed"
								: "bg-amber-200 text-slate-800 border-amber-400 hover:bg-amber-300 hover:border-amber-500 hover:cursor-pointer"
						}`}
					>
						{loadingMore ? "Loading..." : "See More"}
					</button>
				</div>
			)}
		</div>
	);
};

export default NewsSection;

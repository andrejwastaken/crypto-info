import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Spinner from "../components/Spinner";
import { useCoins } from "../context/CoinsContext";
import { formatNumber, formatNumberChainMetrics } from "../helpers";

type SortField =
	| "name"
	| "marketCap"
	| "volume"
	| "circulatingSupply"
	| "change52w";

type Prediction = {
	symbol: string;
	predictedClose: number;
	predictedChangePct: number;
};

type PredictionsData = {
	top: Prediction[];
	bottom: Prediction[];
};

type ChainSentimentPrediction = {
	id: number;
	symbol: string;
	date: string;
	predictedClose: number;
	predictedChangePct: number;
};

type OnChainMetric = {
	id: number;
	symbol: string;
	date: string;
	activeAddresses: number;
	transactions: number;
	exchangeInflow: number;
	exchangeOutflow: number;
	whaleTransactions: number;
	nvtRatio: number;
	mvrvRatio: number;
	netFlow: number;
	securityValue: number;
	tvlUsd: number;
};

const LandingPage = () => {
	const navigate = useNavigate();
	const { coins, loading } = useCoins();
	const [pageSize, setPageSize] = useState(25);
	const [currentPage, setCurrentPage] = useState(0);
	const [sortBy, setSortBy] = useState<SortField>("marketCap");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
	const [predictions, setPredictions] = useState<PredictionsData | null>(null);
	const [predictionsLoading, setPredictionsLoading] = useState(true);
	const [chainSentimentPredictions, setChainSentimentPredictions] = useState<
		ChainSentimentPrediction[]
	>([]);
	const [chainSentimentLoading, setChainSentimentLoading] = useState(true);
	const [onChainMetrics, setOnChainMetrics] = useState<OnChainMetric[]>([]);
	const [onChainLoading, setOnChainLoading] = useState(true);

	useEffect(() => {
		const fetchPredictions = async () => {
			try {
				const response = await fetch(
					"http://localhost:8080/api/prediction/extremes"
				);
				if (response.ok) {
					const data = await response.json();
					setPredictions(data);
				}
			} catch (error) {
				console.error("Failed to fetch predictions:", error);
			} finally {
				setPredictionsLoading(false);
			}
		};

		const fetchChainSentimentPredictions = async () => {
			try {
				const response = await fetch(
					"http://localhost:8080/api/chain-sentiment-prediction"
				);
				if (response.ok) {
					const data = await response.json();
					setChainSentimentPredictions(data);
				}
			} catch (error) {
				console.error("Failed to fetch chain-sentiment predictions:", error);
			} finally {
				setChainSentimentLoading(false);
			}
		};

		const fetchOnChainMetrics = async () => {
			try {
				const response = await fetch("http://localhost:8080/api/on-chain");
				if (response.ok) {
					const data = await response.json();
					setOnChainMetrics(data);
				}
			} catch (error) {
				console.error("Failed to fetch on-chain metrics:", error);
			} finally {
				setOnChainLoading(false);
			}
		};

		fetchPredictions();
		fetchChainSentimentPredictions();
		fetchOnChainMetrics();
	}, []);

	const sortedCoins = useMemo(() => {
		return [...coins].sort((a, b) => {
			if (sortBy === "name") {
				const aName = a.name?.toLowerCase() ?? "";
				const bName = b.name?.toLowerCase() ?? "";
				const result = aName.localeCompare(bName);
				return sortOrder === "desc" ? -result : result;
			}

			const aVal = a[sortBy] ?? 0;
			const bVal = b[sortBy] ?? 0;
			return sortOrder === "desc" ? bVal - aVal : aVal - bVal;
		});
	}, [coins, sortBy, sortOrder]);

	const totalPages = Math.ceil(sortedCoins.length / pageSize);
	const paginatedCoins = sortedCoins.slice(
		currentPage * pageSize,
		(currentPage + 1) * pageSize
	);

	const handlePageSizeChange = (newSize: number) => {
		setPageSize(newSize);
		setCurrentPage(0);
	};

	if (loading) {
		return (
			<div className="min-h-screen bg-slate-800">
				<div className="container mx-auto px-4 py-8 flex items-center justify-center">
					<Spinner size="lg" color="amber" />
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-slate-800">
			<div className="container mx-auto px-4 py-8">
				{/* predictions and on-chain metrics section */}
				<div className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
					{/* predictions section */}
					{!predictionsLoading && predictions && (
						<div className="bg-amber-100 border border-amber-400 rounded-lg shadow-sm p-4">
							<div className="flex items-center justify-center gap-2 mb-3">
								<h2 className="text-2xl font-bold text-slate-800">
									Tomorrow's AI Predictions
								</h2>
								<div className="group/tooltip relative flex items-center">
									<svg
										className="w-4 h-4 cursor-help text-gray-400"
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
									<div className="hidden group-hover/tooltip:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-gray-800 text-white rounded text-[10px] z-10 shadow-lg text-center">
										This prediction is made using an LSTM model. For more
										details, visit the{" "}
										<span className="font-bold">How it works?</span> page.
									</div>
								</div>
							</div>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
									<h3 className="text-base font-semibold text-green-600 mb-2">
										Top 5 Predicted Winners
									</h3>
									<div className="space-y-1.5">
										{predictions.top.map((pred, idx) => (
											<div
												key={pred.symbol}
												className="flex items-center justify-between p-2.5 bg-green-50 rounded border border-green-200 hover:bg-green-100 transition-colors cursor-pointer"
												onClick={() => navigate(`/coins/${pred.symbol}`)}
											>
												<div className="flex items-center gap-2">
													<span className="text-xs font-semibold text-gray-500 w-5">
														#{idx + 1}
													</span>
													<span className="font-medium text-gray-900 text-sm">
														{pred.symbol.replace("-USD", "")}
													</span>
												</div>
												<div className="flex items-center gap-3">
													<span className="text-xs text-gray-600 w-16 text-right">
														${pred.predictedClose.toFixed(2)}
													</span>
													<span className="font-semibold text-green-600 text-sm w-20 text-right">
														+{pred.predictedChangePct.toFixed(2)}%
													</span>
												</div>
											</div>
										))}
									</div>
								</div>

								<div>
									<h3 className="text-base font-semibold text-red-600 mb-2">
										Top 5 Predicted Losers
									</h3>
									<div className="space-y-1.5">
										{predictions.bottom.map((pred, idx) => (
											<div
												key={pred.symbol}
												className="flex items-center justify-between p-2.5 bg-red-50 rounded border border-red-200 hover:bg-red-100 transition-colors cursor-pointer"
												onClick={() => navigate(`/coins/${pred.symbol}`)}
											>
												<div className="flex items-center gap-2">
													<span className="text-xs font-semibold text-gray-500 w-5">
														#{idx + 1}
													</span>
													<span className="font-medium text-gray-900 text-sm">
														{pred.symbol.replace("-USD", "")}
													</span>
												</div>
												<div className="flex items-center gap-3">
													<span className="text-xs text-gray-600 w-16 text-right">
														${pred.predictedClose.toFixed(2)}
													</span>
													<span className="font-semibold text-red-600 text-sm w-20 text-right">
														{pred.predictedChangePct.toFixed(2)}%
													</span>
												</div>
											</div>
										))}
									</div>
								</div>
							</div>

							{/* chain-sentiment predictions table */}
							{!chainSentimentLoading &&
								chainSentimentPredictions.length > 0 && (
									<div className="mt-4 md:w-[calc(50%-0.5rem)] mx-auto">
										<h3 className="text-center font-semibold text-slate-800 mb-2">
											Predictions based on on-chain + sentiment analysis
										</h3>
										<div className="space-y-1.5">
											{chainSentimentPredictions.map((pred) => (
												<div
													key={pred.id}
													className={`flex items-center justify-between p-2.5 rounded border transition-colors cursor-pointer ${
														pred.predictedChangePct >= 0
															? "bg-green-50 border-green-200 hover:bg-green-100"
															: "bg-red-50 border-red-200 hover:bg-red-100"
													}`}
													onClick={() => navigate(`/coins/${pred.symbol}`)}
												>
													<div className="flex items-center gap-2">
														<span className="font-medium text-gray-900 text-sm">
															{pred.symbol.replace("-USD", "")}
														</span>
													</div>
													<div className="flex items-center gap-3">
														<span className="text-xs text-gray-600 w-16 text-right">
															${pred.predictedClose.toFixed(2)}
														</span>
														<span
															className={`font-semibold text-sm w-20 text-right ${
																pred.predictedChangePct >= 0
																	? "text-green-600"
																	: "text-red-600"
															}`}
														>
															{pred.predictedChangePct >= 0 ? "+" : ""}
															{pred.predictedChangePct.toFixed(2)}%
														</span>
													</div>
												</div>
											))}
										</div>
									</div>
								)}
						</div>
					)}

					{/* on-chain metrics section */}
					{!onChainLoading && onChainMetrics.length > 0 && (
						<div className="bg-amber-100 border border-amber-400 rounded-lg shadow-sm p-4 lg:col-span-1 lg:max-w-none">
							<div className="flex items-center justify-center gap-2 mb-3">
								<h2 className="text-2xl font-bold text-slate-800">
									On-Chain Metrics
								</h2>
								<div className="group/tooltip relative flex items-center">
									<svg
										className="w-4 h-4 cursor-help text-gray-400"
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
									<div className="hidden group-hover/tooltip:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-gray-800 text-white rounded text-[10px] z-10 shadow-lg text-center">
										On-chain metrics provide insights into blockchain activity
										and investor behavior. For more details, visit the{" "}
										<span className="font-bold">How it works?</span> page.
									</div>
								</div>
							</div>
							{/* column headers */}
							<div className="grid grid-cols-11 gap-1 px-3 py-2 text-[10px] font-semibold text-gray-500">
								<div className="col-span-1">Symbol</div>
								<div className="text-right">Active</div>
								<div className="text-right">Txns</div>
								<div className="text-right">Inflow</div>
								<div className="text-right">Outflow</div>
								<div className="text-right">Net Flow</div>
								<div className="text-right">Whale</div>
								<div className="text-right">NVT</div>
								<div className="text-right">MVRV</div>
								<div className="text-right">TVL</div>
								<div className="text-right">Hash Rate</div>
							</div>
							{/* data rows */}
							<div className="space-y-4 flex flex-col">
								{onChainMetrics.map((metric) => (
									<div
										key={metric.symbol}
										className="grid grid-cols-11 gap-1 items-center py-6 px-3 bg-amber-50 rounded border border-amber-300 hover:bg-amber-200 transition-colors cursor-pointer"
										onClick={() => navigate(`/coins/${metric.symbol}`)}
									>
										<div className="col-span-1">
											<span className="font-semibold text-gray-900 text-sm">
												{metric.symbol.replace("-USD", "")}
											</span>
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.activeAddresses
												? formatNumberChainMetrics(metric.activeAddresses)
												: "~0"}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.transactions
												? formatNumberChainMetrics(metric.transactions)
												: "~0"}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.exchangeInflow
												? formatNumberChainMetrics(metric.exchangeInflow)
												: "~0"}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.exchangeOutflow
												? formatNumberChainMetrics(metric.exchangeOutflow)
												: "~0"}
										</div>
										<div
											className={`text-right text-[11px] font-medium ${
												metric.netFlow === 0
													? "text-gray-500"
													: metric.netFlow > 0
													? "text-green-600"
													: "text-red-600"
											}`}
										>
											{metric.netFlow === 0
												? "~0"
												: (metric.netFlow > 0 ? "+" : "") +
												  formatNumberChainMetrics(metric.netFlow)}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.whaleTransactions
												? formatNumberChainMetrics(metric.whaleTransactions)
												: "~0"}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.nvtRatio ? metric.nvtRatio.toFixed(2) : "~0"}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.mvrvRatio ? metric.mvrvRatio.toFixed(2) : "~0"}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.tvlUsd
												? formatNumberChainMetrics(metric.tvlUsd)
												: "~0"}
										</div>
										<div className="text-right text-[11px] text-gray-700">
											{metric.securityValue
												? formatNumberChainMetrics(metric.securityValue)
												: "~0"}
										</div>
									</div>
								))}
							</div>
						</div>
					)}
				</div>

				<div className="bg-amber-100 border border-amber-400 rounded-lg shadow-sm p-4">
					<h2 className="text-2xl font-bold text-slate-800 mb-4">
						All Cryptocurrencies
					</h2>

					<div className="mb-4 flex flex-wrap items-center gap-6">
						<div className="flex items-center gap-2">
							<label className="text-sm font-medium text-slate-800">
								Sort by:
							</label>
							<select
								value={sortBy}
								onChange={(e) => {
									setSortBy(e.target.value as SortField);
									setCurrentPage(0);
								}}
								className="px-4 py-2 border border-amber-300 rounded-md bg-white 
						focus:outline-none focus:ring-2 focus:ring-amber-400"
							>
								<option value="name">Name</option>
								<option value="marketCap">Market Cap</option>
								<option value="volume">Volume</option>
								<option value="circulatingSupply">Circulating Supply</option>
								<option value="change52w">52W Change</option>
							</select>
						</div>
						<div className="flex items-center gap-1">
							<button
								onClick={() => {
									setSortOrder("desc");
									setCurrentPage(0);
								}}
								className={`px-3 py-1 text-sm rounded-lg border border-amber-300 ${
									sortOrder === "desc"
										? "bg-amber-200 border-amber-500"
										: "text-slate-700 hover:bg-amber-200 hover:cursor-pointer"
								}`}
							>
								↓ Desc
							</button>
							<button
								onClick={() => {
									setSortOrder("asc");
									setCurrentPage(0);
								}}
								className={`px-3 py-1 text-sm rounded-lg border border-amber-300 ${
									sortOrder === "asc"
										? "bg-amber-200 border-amber-500"
										: "text-slate-700 hover:bg-amber-200 hover:cursor-pointer"
								}`}
							>
								↑ Asc
							</button>
						</div>
					</div>

					{paginatedCoins.length !== 0 && (
						<>
							<div className="overflow-x-auto">
								<table className="min-w-full bg-amber-50 border border-amber-300 rounded-lg shadow-sm">
									<thead className="bg-amber-200">
										<tr>
											<th className="px-6 py-3 text-left text-sm font-semibold text-slate-800 border-b border-amber-300">
												#
											</th>
											<th className="px-6 py-3 text-left text-sm font-semibold text-slate-800 border-b border-amber-300">
												Symbol
											</th>
											<th className="px-6 py-3 text-left text-sm font-semibold text-slate-800 border-b border-amber-300">
												Name
											</th>
											<th className="px-6 py-3 text-left text-sm font-semibold text-slate-800 border-b border-amber-300">
												Market Cap
											</th>
											<th className="px-6 py-3 text-left text-sm font-semibold text-slate-800 border-b border-amber-300">
												Volume
											</th>
											<th className="px-6 py-3 text-left text-sm font-semibold text-slate-800 border-b border-amber-300">
												Circulating Supply
											</th>
											<th className="px-6 py-3 text-left text-sm font-semibold text-slate-800 border-b border-amber-300">
												52W Change
											</th>
										</tr>
									</thead>
									<tbody>
										{paginatedCoins.map((coin, index) => (
											<tr
												key={coin.id}
												className="hover:bg-amber-100 transition-colors cursor-pointer"
												onClick={() => navigate(`/coins/${coin.symbol}`)}
											>
												<td className="px-6 py-4 text-sm text-slate-900 border-b border-amber-200">
													{currentPage * pageSize + index + 1}.
												</td>
												<td className="px-6 py-4 text-sm text-slate-900 border-b border-amber-200">
													{coin.symbol}
												</td>
												<td className="px-6 py-4 text-sm text-slate-900 border-b border-amber-200">
													{coin.name}
												</td>
												<td className="px-6 py-4 text-sm text-slate-900 border-b border-amber-200">
													{coin.marketCap != null
														? formatNumber(coin.marketCap)
														: "—"}
												</td>
												<td className="px-6 py-4 text-sm text-slate-900 border-b border-amber-200">
													{coin.volume != null
														? formatNumber(coin.volume)
														: "—"}
												</td>
												<td className="px-6 py-4 text-sm text-slate-900 border-b border-amber-200">
													{coin.circulatingSupply != null
														? formatNumber(coin.circulatingSupply)
														: "—"}
												</td>
												<td className="px-6 py-4 text-sm border-b border-amber-200">
													{coin.change52w != null ? (
														<span
															className={
																coin.change52w >= 0
																	? "text-green-600"
																	: "text-red-600"
															}
														>
															{coin.change52w >= 0 ? "+" : ""}
															{coin.change52w.toFixed(2)}%
														</span>
													) : (
														"—"
													)}
												</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>

							{/* pagination handling */}
							<div className="mt-4 flex flex-wrap items-center justify-between gap-4">
								<div className="flex items-center gap-2">
									<span className="text-sm text-slate-800">
										Items per page:
									</span>
									<select
										value={pageSize}
										onChange={(e) =>
											handlePageSizeChange(Number(e.target.value))
										}
										className="px-3 py-1 border border-amber-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
									>
										<option value={25}>25</option>
										<option value={50}>50</option>
										<option value={100}>100</option>
									</select>
								</div>

								<div className="flex items-center gap-1">
									<button
										onClick={() => setCurrentPage(0)}
										disabled={currentPage === 0}
										className="px-3 py-1 text-sm border border-amber-300 rounded-md bg-white hover:bg-amber-100 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
									>
										First
									</button>
									<button
										onClick={() => setCurrentPage((p) => p - 1)}
										disabled={currentPage === 0}
										className="px-3 py-1 text-sm border border-amber-300 rounded-md bg-white hover:bg-amber-100 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
									>
										Prev
									</button>

									<span className="px-4 py-1 text-sm text-slate-800">
										Page {currentPage + 1} of {totalPages}
									</span>

									<button
										onClick={() => setCurrentPage((p) => p + 1)}
										disabled={currentPage >= totalPages - 1}
										className="px-3 py-1 text-sm border border-amber-300 rounded-md bg-white hover:bg-amber-100 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
									>
										Next
									</button>
									<button
										onClick={() => setCurrentPage(totalPages - 1)}
										disabled={currentPage >= totalPages - 1}
										className="px-3 py-1 text-sm border border-amber-300 rounded-md bg-white hover:bg-amber-100 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
									>
										Last
									</button>
								</div>

								<div className="text-sm text-slate-800">
									Total: {sortedCoins.length} items
								</div>
							</div>
						</>
					)}
				</div>
			</div>
		</div>
	);
};

export default LandingPage;

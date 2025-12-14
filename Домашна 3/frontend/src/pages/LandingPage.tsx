import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCoins } from "../context/CoinsContext";
import { formatNumber } from "../helpers";

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

const LandingPage = () => {
	const navigate = useNavigate();
	const { coins, loading } = useCoins();
	const [pageSize, setPageSize] = useState(25);
	const [currentPage, setCurrentPage] = useState(0);
	const [sortBy, setSortBy] = useState<SortField>("marketCap");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
	const [predictions, setPredictions] = useState<PredictionsData | null>(null);
	const [predictionsLoading, setPredictionsLoading] = useState(true);

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
		fetchPredictions();
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
			<div className="container mx-auto px-4 py-8">
				<p className="text-gray-600">Loading coins...</p>
			</div>
		);
	}

	return (
		<div className="container mx-auto px-4 py-8">
			{/* predictions section */}
			{!predictionsLoading && predictions && (
				<div className="mb-8 bg-white border border-gray-300 rounded-lg shadow-sm p-4 max-w-4xl mx-auto">
					<div className="flex items-center justify-center gap-2 mb-3">
						<h2 className="text-2xl font-bold text-gray-800">
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
								This prediction is made using an LSTM model. For more details,
								go to the `XXXXX` page.
							</div>
						</div>
					</div>
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						{/* Top 5 Predictions */}
						<div>
							<h3 className="text-base font-semibold text-green-600 mb-2">
								Top 5 Gainers
							</h3>
							<div className="space-y-1.5">
								{predictions.top.map((pred, idx) => (
									<div
										key={pred.symbol}
										className="flex items-center justify-between p-2 bg-green-50 rounded border border-green-200"
									>
										<div className="flex items-center gap-2">
											<span className="text-xs font-semibold text-gray-500 w-5">
												#{idx + 1}
											</span>
											<Link
												to={`/coins/${pred.symbol}`}
												className="font-medium text-gray-900 text-sm hover:text-green-600 hover:underline"
											>
												{pred.symbol}
											</Link>
										</div>
										<div className="flex items-center gap-3">
											<span className="text-xs text-gray-600">
												${pred.predictedClose.toFixed(2)}
											</span>
											<span className="font-semibold text-green-600 text-sm">
												+{pred.predictedChangePct.toFixed(2)}%
											</span>
										</div>
									</div>
								))}
							</div>
						</div>

						{/* Bottom 5 Predictions */}
						<div>
							<h3 className="text-base font-semibold text-red-600 mb-2">
								Top 5 Losers
							</h3>
							<div className="space-y-1.5">
								{predictions.bottom.map((pred, idx) => (
									<div
										key={pred.symbol}
										className="flex items-center justify-between p-2 bg-red-50 rounded border border-red-200"
									>
										<div className="flex items-center gap-2">
											<span className="text-xs font-semibold text-gray-500 w-5">
												#{idx + 1}
											</span>
											<Link
												to={`/coins/${pred.symbol}`}
												className="font-medium text-gray-900 text-sm hover:text-red-600 hover:underline"
											>
												{pred.symbol}
											</Link>
										</div>
										<div className="flex items-center gap-3">
											<span className="text-xs text-gray-600">
												${pred.predictedClose.toFixed(2)}
											</span>
											<span className="font-semibold text-red-600 text-sm">
												{pred.predictedChangePct.toFixed(2)}%
											</span>
										</div>
									</div>
								))}
							</div>
						</div>
					</div>
				</div>
			)}

			<h2 className="text-2xl font-bold text-gray-800 mb-4">
				All Cryptocurrencies
			</h2>

			<div className="mb-4 flex flex-wrap items-center gap-6">
				<div className="flex items-center gap-2">
					<label className="text-sm font-medium text-gray-700">Sort by:</label>
					<select
						value={sortBy}
						onChange={(e) => {
							setSortBy(e.target.value as SortField);
							setCurrentPage(0);
						}}
						className="px-4 py-2 border border-gray-300 rounded-md bg-white 
						focus:outline-none focus:ring-2 focus:ring-blue-500"
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
						className={`px-3 py-1 text-sm rounded-lg border border-gray-200 ${
							sortOrder === "desc"
								? "bg-gray-100 border-gray-400"
								: "text-gray-600 hover:bg-gray-100 hover:cursor-pointer"
						}`}
					>
						↓ Desc
					</button>
					<button
						onClick={() => {
							setSortOrder("asc");
							setCurrentPage(0);
						}}
						className={`px-3 py-1 text-sm rounded-lg border border-gray-200 ${
							sortOrder === "asc"
								? "bg-gray-100 border-gray-400"
								: "text-gray-600 hover:bg-gray-100 hover:cursor-pointer"
						}`}
					>
						↑ Asc
					</button>
				</div>
			</div>

			{paginatedCoins.length !== 0 && (
				<>
					<div className="overflow-x-auto">
						<table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-sm">
							<thead className="bg-gray-100">
								<tr>
									<th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">
										#
									</th>
									<th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">
										Symbol
									</th>
									<th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">
										Name
									</th>
									<th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">
										Market Cap
									</th>
									<th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">
										Volume
									</th>
									<th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">
										Circulating Supply
									</th>
									<th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">
										52W Change
									</th>
								</tr>
							</thead>
							<tbody>
								{paginatedCoins.map((coin, index) => (
									<tr
										key={coin.id}
										className="hover:bg-gray-50 transition-colors cursor-pointer"
										onClick={() => navigate(`/coins/${coin.symbol}`)}
									>
										<td className="px-6 py-4 text-sm text-gray-900 border-b">
											{currentPage * pageSize + index + 1}
										</td>
										<td className="px-6 py-4 text-sm text-gray-900 border-b">
											{coin.symbol}
										</td>
										<td className="px-6 py-4 text-sm text-gray-900 border-b">
											{coin.name}
										</td>
										<td className="px-6 py-4 text-sm text-gray-900 border-b">
											{coin.marketCap != null
												? formatNumber(coin.marketCap)
												: "—"}
										</td>
										<td className="px-6 py-4 text-sm text-gray-900 border-b">
											{coin.volume != null ? formatNumber(coin.volume) : "—"}
										</td>
										<td className="px-6 py-4 text-sm text-gray-900 border-b">
											{coin.circulatingSupply != null
												? formatNumber(coin.circulatingSupply)
												: "—"}
										</td>
										<td className="px-6 py-4 text-sm border-b">
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
							<span className="text-sm text-gray-700">Items per page:</span>
							<select
								value={pageSize}
								onChange={(e) => handlePageSizeChange(Number(e.target.value))}
								className="px-3 py-1 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
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
								className="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							>
								First
							</button>
							<button
								onClick={() => setCurrentPage((p) => p - 1)}
								disabled={currentPage === 0}
								className="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Prev
							</button>

							<span className="px-4 py-1 text-sm text-gray-700">
								Page {currentPage + 1} of {totalPages}
							</span>

							<button
								onClick={() => setCurrentPage((p) => p + 1)}
								disabled={currentPage >= totalPages - 1}
								className="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Next
							</button>
							<button
								onClick={() => setCurrentPage(totalPages - 1)}
								disabled={currentPage >= totalPages - 1}
								className="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Last
							</button>
						</div>

						<div className="text-sm text-gray-600">
							Total: {sortedCoins.length} items
						</div>
					</div>
				</>
			)}
		</div>
	);
};

export default LandingPage;

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCoins } from "../context/CoinsContext";
import { formatNumber } from "../helpers";

type SortField =
	| "name"
	| "marketCap"
	| "volume"
	| "circulatingSupply"
	| "change52w";

const LandingPage = () => {
	const navigate = useNavigate();
	const { coins, loading } = useCoins();
	const [pageSize, setPageSize] = useState(25);
	const [currentPage, setCurrentPage] = useState(0);
	const [sortBy, setSortBy] = useState<SortField>("marketCap");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

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

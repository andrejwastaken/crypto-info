import { useNavigate } from "react-router-dom";
import { formatNumber } from "../helpers";
import type { Coin, SortField } from "../types";

type CryptoTableProps = {
	sortedCoins: Coin[];
	pageSize: number;
	currentPage: number;
	sortBy: SortField;
	sortOrder: "asc" | "desc";
	onPageSizeChange: (size: number) => void;
	onSortByChange: (field: SortField) => void;
	onSortOrderChange: (order: "asc" | "desc") => void;
	onPageChange: (page: number) => void;
};

const CryptoTable = ({
	sortedCoins,
	pageSize,
	currentPage,
	sortBy,
	sortOrder,
	onPageSizeChange,
	onSortByChange,
	onSortOrderChange,
	onPageChange,
}: CryptoTableProps) => {
	const navigate = useNavigate();

	const totalPages = Math.ceil(sortedCoins.length / pageSize);
	const paginatedCoins = sortedCoins.slice(
		currentPage * pageSize,
		(currentPage + 1) * pageSize
	);

	return (
		<div className="bg-amber-100 border border-amber-400 rounded-lg shadow-sm p-4">
			<h2 className="text-2xl font-bold text-slate-800 mb-4">
				All Cryptocurrencies
			</h2>

			<div className="mb-4 flex flex-wrap items-center gap-6">
				<div className="flex items-center gap-2">
					<label className="text-sm font-medium text-slate-800">Sort by:</label>
					<select
						value={sortBy}
						onChange={(e) => {
							onSortByChange(e.target.value as SortField);
							onPageChange(0);
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
							onSortOrderChange("desc");
							onPageChange(0);
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
							onSortOrderChange("asc");
							onPageChange(0);
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
											{coin.volume != null ? formatNumber(coin.volume) : "—"}
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
							<span className="text-sm text-slate-800">Items per page:</span>
							<select
								value={pageSize}
								onChange={(e) => onPageSizeChange(Number(e.target.value))}
								className="px-3 py-1 border border-amber-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
							>
								<option value={25}>25</option>
								<option value={50}>50</option>
								<option value={100}>100</option>
							</select>
						</div>

						<div className="flex items-center gap-1">
							<button
								onClick={() => onPageChange(0)}
								disabled={currentPage === 0}
								className="px-3 py-1 text-sm border border-amber-300 rounded-md bg-white hover:bg-amber-100 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							>
								First
							</button>
							<button
								onClick={() => onPageChange(currentPage - 1)}
								disabled={currentPage === 0}
								className="px-3 py-1 text-sm border border-amber-300 rounded-md bg-white hover:bg-amber-100 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Prev
							</button>

							<span className="px-4 py-1 text-sm text-slate-800">
								Page {currentPage + 1} of {totalPages}
							</span>

							<button
								onClick={() => onPageChange(currentPage + 1)}
								disabled={currentPage >= totalPages - 1}
								className="px-3 py-1 text-sm border border-amber-300 rounded-md bg-white hover:bg-amber-100 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Next
							</button>
							<button
								onClick={() => onPageChange(totalPages - 1)}
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
	);
};

export default CryptoTable;

import { formatNumber, formatPrice } from "../helpers";
import type { CoinStats } from "../types";

type HistoricStatsProps = {
	coinStats: CoinStats | null;
	statsLoading: boolean;
};

const HistoricStats = ({ coinStats, statsLoading }: HistoricStatsProps) => {
	if (statsLoading) {
		return (
			<div className="mt-6 bg-amber-100 rounded-lg border border-amber-400 shadow-sm p-6">
				<div className="animate-pulse space-y-4">
					<div className="h-6 w-32 bg-amber-200 rounded mx-auto"></div>
					<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
						{[...Array(3)].map((_, i) => (
							<div key={i} className="space-y-2">
								{[...Array(3)].map((_, j) => (
									<div key={j} className="flex justify-between">
										<div className="h-4 w-20 bg-amber-200 rounded"></div>
										<div className="h-4 w-24 bg-amber-200 rounded"></div>
									</div>
								))}
							</div>
						))}
					</div>
				</div>
			</div>
		);
	}

	if (!coinStats) {
		return null;
	}

	return (
		<div className="mt-6 bg-amber-100 rounded-lg border border-amber-400 shadow-sm p-6">
			<h3 className="text-lg font-semibold text-slate-800 mb-4 text-center">
				Historic Statistics
			</h3>
			<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
				{/* 24h stats */}
				<div className="text-center">
					<h4 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wider">
						24 Hour
					</h4>
					<div className="space-y-2 text-sm">
						<div className="flex justify-between">
							<span className="text-slate-600">Low:</span>
							<span className="font-medium">
								{coinStats.low24h != null ? formatPrice(coinStats.low24h) : "—"}
							</span>
						</div>
						<div className="flex justify-between">
							<span className="text-slate-600">High:</span>
							<span className="font-medium">
								{coinStats.high24h != null
									? formatPrice(coinStats.high24h)
									: "—"}
							</span>
						</div>
						<div className="flex justify-between">
							<span className="text-slate-600">Volume:</span>
							<span className="font-medium">
								{coinStats.volume24h != null
									? formatNumber(coinStats.volume24h)
									: "—"}
							</span>
						</div>
					</div>
				</div>

				{/* 52w stats */}
				<div className="text-center">
					<h4 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wider">
						52 Week
					</h4>
					<div className="space-y-2 text-sm">
						<div className="flex justify-between">
							<span className="text-slate-600">Low:</span>
							<span className="font-medium">
								{coinStats.low52w != null ? formatPrice(coinStats.low52w) : "—"}
							</span>
						</div>
						<div className="flex justify-between">
							<span className="text-slate-600">High:</span>
							<span className="font-medium">
								{coinStats.high52w != null
									? formatPrice(coinStats.high52w)
									: "—"}
							</span>
						</div>
					</div>
				</div>

				{/* open/close stats */}
				<div className="text-center">
					<h4 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wider">
						Price Points
					</h4>
					<div className="space-y-2 text-sm">
						<div className="flex justify-between">
							<span className="text-slate-600">Open:</span>
							<span className="font-medium">
								{coinStats.open != null ? formatPrice(coinStats.open) : "—"}
							</span>
						</div>
						<div className="flex justify-between">
							<span className="text-slate-600">Current:</span>
							<span className="font-medium">
								{coinStats.close != null ? formatPrice(coinStats.close) : "—"}
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

export default HistoricStats;

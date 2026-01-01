import { formatNumber, formatPrice } from "../helpers";
import type { AnalysisTimePeriod, TechnicalAnalysisStats } from "../types";

type TechnicalAnalysisIndicatorsProps = {
	taStats: Record<AnalysisTimePeriod, TechnicalAnalysisStats | null>;
	taStatsPeriod: AnalysisTimePeriod;
	taStatsLoading: boolean;
	onPeriodChange: (period: AnalysisTimePeriod) => void;
};

const TechnicalAnalysisIndicators = ({
	taStats,
	taStatsPeriod,
	taStatsLoading,
	onPeriodChange,
}: TechnicalAnalysisIndicatorsProps) => {
	return (
		<div className="mt-6 bg-amber-100 rounded-lg border border-amber-400 shadow-sm p-6">
			<div className="flex items-center justify-center gap-4 mb-4">
				<h3 className="text-lg font-semibold text-slate-800">
					Technical Analysis Indicators
				</h3>
				<div className="flex gap-2">
					{(["DAY", "WEEK", "MONTH"] as AnalysisTimePeriod[]).map((p) => (
						<button
							key={p}
							onClick={() => onPeriodChange(p)}
							className={`px-3 py-1 text-xs rounded-lg border border-amber-300 ${
								taStatsPeriod === p
									? "bg-amber-200 border-amber-500 font-medium"
									: "text-slate-600 hover:bg-amber-200 hover:cursor-pointer"
							}`}
						>
							{p === "DAY" ? "1D" : p === "WEEK" ? "1W" : "1M"}
						</button>
					))}
				</div>
			</div>

			{taStatsLoading ? (
				<div className="animate-pulse space-y-4">
					<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
						{[...Array(3)].map((_, i) => (
							<div key={i} className="space-y-2">
								{[...Array(4)].map((_, j) => (
									<div key={j} className="flex justify-between">
										<div className="h-4 w-32 bg-amber-200 rounded"></div>
										<div className="h-4 w-24 bg-amber-200 rounded"></div>
									</div>
								))}
							</div>
						))}
					</div>
				</div>
			) : taStats[taStatsPeriod] ? (
				<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
					{/* Oscillators */}
					<div className="text-center">
						<h4 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wider">
							Oscillators
						</h4>
						<div className="space-y-2 text-sm">
							<div className="flex justify-between">
								<span className="text-slate-600">RSI:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.rsi != null
										? taStats[taStatsPeriod]!.rsi.toFixed(2)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">Stochastic K:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.stochK != null
										? taStats[taStatsPeriod]!.stochK.toFixed(2)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">Stochastic D:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.stochD != null
										? taStats[taStatsPeriod]!.stochD.toFixed(2)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">CCI:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.cci != null
										? taStats[taStatsPeriod]!.cci.toFixed(2)
										: "N/A"}
								</span>
							</div>
						</div>
					</div>

					{/* MACD & DMI */}
					<div className="text-center">
						<h4 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wider">
							MACD & DMI
						</h4>
						<div className="space-y-2 text-sm">
							<div className="flex justify-between">
								<span className="text-slate-600">MACD Line:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.macdLine != null
										? taStats[taStatsPeriod]!.macdLine.toFixed(2)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">MACD Signal:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.macdSignal != null
										? taStats[taStatsPeriod]!.macdSignal.toFixed(2)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">DMI Plus:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.dmiPlus != null
										? taStats[taStatsPeriod]!.dmiPlus.toFixed(2)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">DMI Minus:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.dmiMinus != null
										? taStats[taStatsPeriod]!.dmiMinus.toFixed(2)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">ADX:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.adx != null
										? taStats[taStatsPeriod]!.adx.toFixed(2)
										: "N/A"}
								</span>
							</div>
						</div>
					</div>

					{/* Moving Averages */}
					<div className="text-center">
						<h4 className="text-sm font-semibold text-slate-600 mb-3 uppercase tracking-wider">
							Moving Averages
						</h4>
						<div className="space-y-2 text-sm">
							<div className="flex justify-between">
								<span className="text-slate-600">SMA:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.sma != null
										? formatPrice(taStats[taStatsPeriod]!.sma)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">EMA:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.ema != null
										? formatPrice(taStats[taStatsPeriod]!.ema)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">WMA:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.wma != null
										? formatPrice(taStats[taStatsPeriod]!.wma)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">Bollinger Middle:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.bollingerMiddle != null
										? formatPrice(taStats[taStatsPeriod]!.bollingerMiddle)
										: "N/A"}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-slate-600">Volume SMA:</span>
								<span className="font-medium">
									{taStats[taStatsPeriod]?.volumeSma != null
										? formatNumber(taStats[taStatsPeriod]!.volumeSma)
										: "N/A"}
								</span>
							</div>
						</div>
					</div>
				</div>
			) : taStats[taStatsPeriod] === null ? (
				<div className="text-center text-slate-600 py-4">
					Not enough data to calculate indicators for this period
				</div>
			) : (
				<div className="text-center text-slate-600 py-4">
					No technical analysis data available
				</div>
			)}
		</div>
	);
};

export default TechnicalAnalysisIndicators;

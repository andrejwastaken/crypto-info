import GaugeComponent from "react-gauge-component";
import { SIGNAL_ZONES } from "../constants/coinPageConstants";
import { formatPrice } from "../helpers";
import type { AnalysisTimePeriod, CoinStats, PredictionData } from "../types";
import Spinner from "./Spinner";

type TechnicalAnalysisGaugeProps = {
	taScores: Record<AnalysisTimePeriod, number | null>;
	taPeriod: AnalysisTimePeriod;
	taLoading: boolean;
	prediction: PredictionData | null;
	coinStats: CoinStats | null;
	onPeriodChange: (period: AnalysisTimePeriod) => void;
};

const TechnicalAnalysisGauge = ({
	taScores,
	taPeriod,
	taLoading,
	prediction,
	coinStats,
	onPeriodChange,
}: TechnicalAnalysisGaugeProps) => {
	const getSignalInfo = (score: number) => {
		const scorePercent = score * 100;
		const zone = SIGNAL_ZONES.find((z) => scorePercent <= z.limit);
		return (
			zone || {
				label: "Strong Buy",
				color: "text-green-600",
			}
		);
	};

	const currentScore = taScores[taPeriod] ?? 0;
	// map [-1, 1] range to [0, 1] for the gauge and signal zones
	const mappedScore = (currentScore + 1) / 2;
	const signalInfo = getSignalInfo(mappedScore);

	return (
		<div className="lg:w-64 shrink-0">
			<div className="bg-amber-100 rounded-lg border border-amber-400 p-4 shadow-sm h-full flex flex-col">
				<h3 className="text-sm font-semibold text-slate-600 mb-4 uppercase tracking-wider text-center">
					Technical Analysis
				</h3>

				<div className="flex justify-center gap-2 mb-4">
					{(["DAY", "WEEK", "MONTH"] as AnalysisTimePeriod[]).map((p) => (
						<button
							key={p}
							onClick={() => onPeriodChange(p)}
							className={`px-3 py-1 text-xs rounded-lg border border-amber-300 ${
								taPeriod === p
									? "bg-amber-200 border-amber-500 font-medium"
									: "text-slate-600 hover:bg-amber-200 hover:cursor-pointer"
							}`}
						>
							{p === "DAY" ? "1D" : p === "WEEK" ? "1W" : "1M"}
						</button>
					))}
				</div>

				{taLoading ? (
					<div className="h-40 flex items-center justify-center">
						<Spinner size="md" color="amber" />
					</div>
				) : (
					<>
						<div className="relative w-full flex justify-center items-end overflow-hidden pb-4">
							<GaugeComponent
								type="semicircle"
								arc={{
									width: 0.2,
									padding: 0.005,
									cornerRadius: 1,
									subArcs: SIGNAL_ZONES.map((zone) => ({
										limit: zone.limit,
										color: zone.gaugeColor,
										showTick: zone.showTick,
									})),
								}}
								pointer={{
									color: "#345243",
									length: 0.75,
									width: 20,
								}}
								labels={{
									valueLabel: { hide: true },
									tickLabels: {
										hideMinMax: true,
									},
								}}
								value={mappedScore * 100}
								minValue={0}
								maxValue={100}
							/>

							<div className="absolute bottom-0 left-0 w-full text-center -mb-0.5">
								<span className={`text-lg font-bold ${signalInfo.color}`}>
									{signalInfo.label}
								</span>
							</div>
						</div>
						<div className="flex items-center justify-center gap-1 mt-2 text-xs text-slate-500">
							<span>Score: {mappedScore.toFixed(2)}</span>
							<div className="group/tooltip relative flex items-center">
								<svg
									className="w-3 h-3 cursor-help"
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
								<div
									className="hidden group-hover/tooltip:block absolute bottom-full left-1/2 
							-translate-x-1/2 mb-2 w-48 p-2 bg-gray-800 text-white rounded text-[10px] 
							z-10 shadow-lg text-center font-light"
								>
									The signal score is calculated using oscilator and moving
									average metrics over the specified period. For more details,
									visit the <span className="font-bold">How it works?</span>{" "}
									page.
								</div>
							</div>
						</div>
						<p className="mt-2 text-xs text-center text-slate-500 italic">
							This is not financial advice
						</p>
					</>
				)}

				<div className="mt-4 p-4 bg-linear-to-br from-amber-50 to-amber-100 rounded-xl border border-amber-300 shadow-sm relative overflow-visible">
					<h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2 text-center">
						Tomorrow's Prediction
					</h4>
					{prediction &&
					coinStats &&
					coinStats.close &&
					prediction.price != 0.0 &&
					prediction.price != 1.0 ? (
						<div className="flex flex-col items-center justify-center">
							<span className="text-2xl font-bold text-slate-900">
								{formatPrice(prediction.price)}
							</span>
							<span
								className={`text-sm font-semibold flex items-center gap-1 mt-1 ${
									prediction.price >= coinStats.close
										? "text-green-600"
										: "text-red-500"
								}`}
							>
								{prediction.price >= coinStats.close ? "+" : ""}
								{(
									((prediction.price - coinStats.close) / coinStats.close) *
									100
								).toFixed(2)}
								%
								<div className="group/tooltip relative flex items-center text-slate-500">
									<svg
										className="w-3 h-3 cursor-help"
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
									<div
										className="hidden group-hover/tooltip:block absolute bottom-full left-1/2 
								-translate-x-1/2 mb-2 w-48 p-2 bg-gray-800 text-white 
								rounded text-[10px] z-10 shadow-lg text-center font-light"
									>
										This prediction is made using an LSTM model. For more
										details, visit the{" "}
										<span className="font-bold">How it works?</span> page.
									</div>
								</div>
							</span>
						</div>
					) : (
						<div className="flex items-center justify-center py-2">
							<span className="text-sm text-slate-600">
								No prediction available
							</span>
						</div>
					)}
				</div>
			</div>
		</div>
	);
};

export default TechnicalAnalysisGauge;

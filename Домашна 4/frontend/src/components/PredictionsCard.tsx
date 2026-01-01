import { useNavigate } from "react-router-dom";
import type { ChainSentimentPrediction, PredictionsData } from "../types";
import Spinner from "./Spinner";

type PredictionsCardProps = {
	predictions: PredictionsData | null;
	predictionsLoading: boolean;
	chainSentimentPredictions: ChainSentimentPrediction[];
	chainSentimentLoading: boolean;
};

const PredictionsCard = ({
	predictions,
	predictionsLoading,
	chainSentimentPredictions,
	chainSentimentLoading,
}: PredictionsCardProps) => {
	const navigate = useNavigate();

	if (predictionsLoading) {
		return (
			<div className="bg-amber-100 border border-amber-400 rounded-lg shadow-sm p-4 flex items-center justify-center h-full">
				<Spinner size="md" color="amber" />
			</div>
		);
	}

	if (!predictions) {
		return null;
	}

	return (
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
						This prediction is made using an LSTM model. For more details, visit
						the <span className="font-bold">How it works?</span> page.
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
			{!chainSentimentLoading && chainSentimentPredictions.length > 0 && (
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
	);
};

export default PredictionsCard;

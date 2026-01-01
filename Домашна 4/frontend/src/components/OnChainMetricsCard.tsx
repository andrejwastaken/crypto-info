import { useNavigate } from "react-router-dom";
import { formatNumberChainMetrics } from "../helpers";
import type { OnChainMetric } from "../types";
import Spinner from "./Spinner";

type OnChainMetricsCardProps = {
	onChainMetrics: OnChainMetric[];
	onChainLoading: boolean;
};

const OnChainMetricsCard = ({
	onChainMetrics,
	onChainLoading,
}: OnChainMetricsCardProps) => {
	const navigate = useNavigate();

	if (onChainLoading) {
		return (
			<div className="bg-amber-100 border border-amber-400 rounded-lg shadow-sm p-4 flex items-center justify-center h-full">
				<Spinner size="md" color="amber" />
			</div>
		);
	}

	if (onChainMetrics.length === 0) {
		return null;
	}

	return (
		<div className="bg-amber-100 border border-amber-400 rounded-lg shadow-sm p-4 lg:col-span-1 lg:max-w-none">
			<div className="flex items-center justify-center gap-2 mb-3">
				<h2 className="text-2xl font-bold text-slate-800">On-Chain Metrics</h2>
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
						On-chain metrics provide insights into blockchain activity and
						investor behavior. For more details, visit the{" "}
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
							{metric.tvlUsd ? formatNumberChainMetrics(metric.tvlUsd) : "~0"}
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
	);
};

export default OnChainMetricsCard;

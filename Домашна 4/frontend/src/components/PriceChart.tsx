import {
	Bar,
	Cell,
	ComposedChart,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
import { formatPrice } from "../helpers";
import type { ChartType, MergedCandleData, TimePeriod } from "../types";
import Spinner from "./Spinner";

type PriceChartProps = {
	chartData: { date: string; close: number }[];
	mergedCandleData: MergedCandleData[];
	chartType: ChartType;
	period: TimePeriod;
	priceChange: number;
	chartLoading: boolean;
	onChartTypeChange: (type: ChartType) => void;
	onPeriodChange: (period: TimePeriod) => void;
};

const PriceChart = ({
	chartData,
	mergedCandleData,
	chartType,
	period,
	priceChange,
	chartLoading,
	onChartTypeChange,
	onPeriodChange,
}: PriceChartProps) => {
	return (
		<div className="flex-1 flex flex-col">
			<div className="flex items-center justify-between mb-4">
				<div className="flex items-center gap-2">
					<button
						onClick={() => onChartTypeChange("line")}
						className={`p-2 rounded-lg border border-amber-300 group ${
							chartType === "line"
								? "bg-amber-200 border-amber-500"
								: "text-amber-100 hover:bg-amber-200 hover:cursor-pointer"
						}`}
						title="Line chart"
					>
						<svg
							width="20"
							height="20"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
							className="group-hover:stroke-slate-900"
						>
							<polyline points="22,6 12,13 7,9 2,15" />
						</svg>
					</button>
					<button
						onClick={() => {
							onChartTypeChange("candle");
							if (period === "7D") onPeriodChange("1M");
						}}
						className={`p-2 rounded-lg border border-amber-300 group ${
							chartType === "candle"
								? "bg-amber-200 border-amber-500"
								: "text-amber-100 hover:bg-amber-200 hover:cursor-pointer"
						}`}
						title="Candlestick chart"
					>
						<svg
							width="20"
							height="20"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
							className="group-hover:stroke-slate-900"
						>
							<line x1="6" y1="4" x2="6" y2="20" />
							<rect
								x="4"
								y="8"
								width="4"
								height="8"
								fill="currentColor"
								className="group-hover:fill-slate-900"
							/>
							<line x1="18" y1="4" x2="18" y2="20" />
							<rect x="16" y="6" width="4" height="10" fill="none" />
						</svg>
					</button>
				</div>

				<div className="flex items-center gap-1">
					{(chartType === "candle"
						? (["1M", "3M", "1Y", "Max"] as TimePeriod[])
						: (["7D", "1M", "3M", "1Y", "Max"] as TimePeriod[])
					).map((p) => (
						<button
							key={p}
							onClick={() => onPeriodChange(p)}
							className={`px-3 py-1 text-sm rounded-lg border border-amber-300 ${
								period === p
									? "bg-amber-200 border-amber-500"
									: "text-amber-100 hover:bg-amber-200 hover:cursor-pointer hover:text-slate-900"
							}`}
						>
							{p}
						</button>
					))}
				</div>
			</div>

			<div className="bg-amber-100 rounded-lg border border-amber-400 shadow-sm p-4 flex-1">
				{chartLoading ? (
					<div className="h-80 flex items-center justify-center">
						<Spinner size="md" color="amber" />
					</div>
				) : (
					<ResponsiveContainer width="100%" height={380}>
						{chartType === "line" ? (
							<LineChart data={chartData}>
								<XAxis
									dataKey="date"
									tick={{ fontSize: 12 }}
									tickFormatter={(value) => {
										const date = new Date(value);
										return date.toLocaleDateString("en-US", {
											month: "short",
											day: "numeric",
										});
									}}
								/>
								<YAxis
									domain={["auto", "auto"]}
									tick={{ fontSize: 12 }}
									tickFormatter={(value) => formatPrice(value)}
									width={80}
								/>
								<Tooltip
									formatter={(value: number) => [
										formatPrice(value ?? 0),
										"Close",
									]}
									labelFormatter={(label) =>
										new Date(label).toLocaleDateString().replace(/-/g, "/")
									}
								/>
								<Line
									type="monotone"
									dataKey="close"
									stroke={priceChange >= 0 ? "#16a34a" : "#dc2626"}
									strokeWidth={1.5}
									dot={false}
								/>
							</LineChart>
						) : (
							<ComposedChart
								data={mergedCandleData}
								barGap={-5}
								barCategoryGap="5%"
							>
								<XAxis
									dataKey="date"
									tick={{ fontSize: 12 }}
									tickFormatter={(value) => {
										const date = new Date(value);
										return date.toLocaleDateString("en-US", {
											month: "short",
											day: "numeric",
										});
									}}
								/>
								<YAxis
									domain={["auto", "auto"]}
									tick={{ fontSize: 12 }}
									tickFormatter={(value) => formatPrice(value)}
									width={80}
								/>
								<Tooltip
									content={({ active, payload }) => {
										if (active && payload && payload.length > 0) {
											const data = payload[0].payload;
											return (
												<div className="bg-white border border-gray-300 rounded p-2 shadow-lg text-sm">
													<p className="font-medium">{data.dateRange}</p>
													<p>Open: {formatPrice(data.open)}</p>
													<p>High: {formatPrice(data.high)}</p>
													<p>Low: {formatPrice(data.low)}</p>
													<p>Close: {formatPrice(data.close)}</p>
												</div>
											);
										}
										return null;
									}}
								/>
								{/* wick - high-low line */}
								<Bar dataKey="highLow" barSize={2} fill="#374151">
									{mergedCandleData.map((entry, index) => (
										<Cell
											key={`wick-${index}`}
											fill={entry.isUp ? "#16a34a" : "#dc2626"}
										/>
									))}
								</Bar>
								{/* body - open-close bar */}
								<Bar dataKey="openClose" barSize={10}>
									{mergedCandleData.map((entry, index) => (
										<Cell
											key={`body-${index}`}
											fill={entry.isUp ? "#16a34a" : "#dc2626"}
										/>
									))}
								</Bar>
							</ComposedChart>
						)}
					</ResponsiveContainer>
				)}
			</div>
		</div>
	);
};

export default PriceChart;

import { useEffect, useState } from "react";
import GaugeComponent from "react-gauge-component";
import { useParams } from "react-router-dom";
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
import { formatNumber, formatPrice } from "../helpers";
import type { CoinStats, OhlcvData } from "../types";

type TimePeriod = "7D" | "1M" | "3M" | "1Y" | "Max";
type ChartType = "line" | "candle";

const periodToSize: Record<TimePeriod, number | null> = {
	"7D": 7,
	"1M": 30,
	"3M": 90,
	"1Y": 365,
	Max: null, // no limit
};

const SIGNAL_ZONES = [
	{
		limit: 15,
		label: "Strong Sell",
		color: "text-red-600",
		gaugeColor: "#DC2626",
		showTick: true,
	},
	{
		limit: 35,
		label: "Sell",
		color: "text-red-500",
		gaugeColor: "#EF4444",
		showTick: true,
	},
	{
		limit: 65,
		label: "Hold",
		color: "text-yellow-500",
		gaugeColor: "#F59E0B",
		showTick: true,
	},
	{
		limit: 85,
		label: "Buy",
		color: "text-green-500",
		gaugeColor: "#22C55E",
		showTick: true,
	},
	{
		limit: 100,
		label: "Strong Buy",
		color: "text-green-600",
		gaugeColor: "#16A34A",
		showTick: false,
	},
];

const CoinPage = () => {
	const { symbol } = useParams<{ symbol: string }>();
	const [coinData, setCoinData] = useState<OhlcvData[]>([]);
	const [coinStats, setCoinStats] = useState<CoinStats | null>(null);
	const [period, setPeriod] = useState<TimePeriod>("1Y");
	const [chartType, setChartType] = useState<ChartType>("line");
	const [chartLoading, setChartLoading] = useState(true);
	const [statsLoading, setStatsLoading] = useState(true);

	const technicalAnalysis = {
		score: 0.13,
		signal: "Not important",
	};

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

	const signalInfo = getSignalInfo(technicalAnalysis.score);

	// fetch stats only once on initial load
	useEffect(() => {
		const fetchStats = async () => {
			if (!symbol) return;
			setStatsLoading(true);

			try {
				const res = await fetch(
					`http://localhost:8080/api/ohlcv-data/${symbol}/stats`
				);
				if (res.ok) {
					const data = await res.json();
					setCoinStats(data);
				}
			} catch (error) {
				console.error("Failed to fetch coin stats:", error);
			} finally {
				setStatsLoading(false);
			}
		};

		fetchStats();
	}, [symbol]);

	// fetch chart data when period changes
	useEffect(() => {
		const fetchChartData = async () => {
			if (!symbol) return;
			setChartLoading(true);

			const size = periodToSize[period];
			const sizeParam = size
				? `?size=${size}&sort=date,desc`
				: "?size=10000&sort=date,desc";

			try {
				const res = await fetch(
					`http://localhost:8080/api/ohlcv-data/${symbol}${sizeParam}`
				);
				const data = await res.json();

				const list: OhlcvData[] = data._embedded?.ohlcvDataList || [];
				// reverse to show oldest first for the chart
				const sortedList = [...list].reverse();
				setCoinData(sortedList);
			} catch (error) {
				console.error("Failed to fetch chart data:", error);
			} finally {
				setChartLoading(false);
			}
		};

		fetchChartData();
	}, [symbol, period]);

	const priceChange =
		coinStats && coinData.length > 1
			? (coinStats.close ?? 0) - coinData[0].close
			: 0;
	const priceChangePercent =
		coinData.length > 1 && coinData[0].close !== 0
			? (priceChange / coinData[0].close) * 100
			: 0;

	// merge consecutive same direction candles for candle chart
	const mergedCandleData = (() => {
		if (coinData.length === 0) return [];

		const result: {
			date: string;
			dateRange: string;
			open: number;
			high: number;
			low: number;
			close: number;
			openClose: [number, number];
			highLow: [number, number];
			isUp: boolean;
		}[] = [];

		let i = 0;
		while (i < coinData.length) {
			const current = coinData[i];
			const isCurrentUp = current.close >= current.open;

			let mergedOpen = current.open;
			let mergedClose = current.close;
			let mergedHigh = current.high;
			let mergedLow = current.low;
			let startDate = current.date;
			let endDate = current.date;

			// look ahead and merge consecutive candles with same direction
			let j = i + 1;
			while (j < coinData.length) {
				const next = coinData[j];
				const isNextUp = next.close >= next.open;

				if (isNextUp === isCurrentUp) {
					// same direction => merge
					mergedClose = next.close;
					mergedHigh = Math.max(mergedHigh, next.high);
					mergedLow = Math.min(mergedLow, next.low);
					endDate = next.date;
					j++;
				} else {
					break;
				}
			}

			result.push({
				date: startDate,
				dateRange:
					startDate === endDate
						? startDate.replace(/-/g, "/")
						: `${startDate.replace(/-/g, "/")} - ${endDate.replace(/-/g, "/")}`,
				open: mergedOpen,
				high: mergedHigh,
				low: mergedLow,
				close: mergedClose,
				openClose: [mergedOpen, mergedClose],
				highLow: [mergedLow, mergedHigh],
				isUp: isCurrentUp,
			});

			i = j;
		}

		return result;
	})();

	const chartData = coinData.map((item) => ({
		date: item.date,
		close: item.close,
	}));

	const coinName = coinStats?.name || symbol || "";

	return (
		<div className="container mx-auto px-4 py-8">
			<div className="mb-6">
				{statsLoading ? (
					<div className="animate-pulse">
						<div className="h-8 w-64 bg-gray-200 rounded mb-2"></div>
						<div className="h-10 w-48 bg-gray-200 rounded"></div>
					</div>
				) : (
					<>
						<h1 className="text-3xl font-light text-gray-800 mb-2">
							{coinName} ({symbol})
						</h1>
						{coinStats && (
							<div className="flex items-baseline gap-3">
								<span className="text-4xl font-semibold text-gray-900">
									{formatPrice(coinStats.close ?? 0)}
								</span>
								<span
									className={`text-xl font-medium ${
										priceChange >= 0 ? "text-green-600" : "text-red-500"
									}`}
								>
									{priceChange >= 0 ? "+" : ""}
									{formatPrice(priceChange)} (
									{priceChangePercent >= 0 ? "+" : ""}
									{priceChangePercent.toFixed(1)}%)
								</span>
							</div>
						)}
					</>
				)}
			</div>

			{/* stats + chart */}
			<div className="flex flex-col lg:flex-row gap-6">
				{/* stats */}
				<div className="lg:w-64 shrink-0">
					{/* technical analysis gauge */}
					<div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm h-full flex flex-col">
						<h3 className="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wider text-center">
							Technical Analysis
						</h3>
						<div className="relative w-full flex justify-center items-end overflow-hidden pb-2">
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
										tooltip: {
											text: zone.label,
										},
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
								value={technicalAnalysis.score * 100}
								minValue={0}
								maxValue={100}
							/>

							<div className="absolute bottom-0 left-0 w-full text-center -mb-0.5">
								<span className={`text-lg font-bold ${signalInfo.color}`}>
									{signalInfo.label}
								</span>
							</div>
						</div>
						<div className="text-center mt-2 text-xs text-gray-400">
							Score: {technicalAnalysis.score.toFixed(2)}
						</div>
						<div className="text-center text-[10px] text-gray-400">
							How do we calculate this?
						</div>

						{statsLoading ? (
							<div className="animate-pulse space-y-4 mt-6">
								<div className="h-6 w-32 bg-gray-200 rounded mx-auto"></div>
								<div className="space-y-2">
									{[...Array(5)].map((_, i) => (
										<div key={i} className="flex justify-between">
											<div className="h-4 w-20 bg-gray-200 rounded"></div>
											<div className="h-4 w-24 bg-gray-200 rounded"></div>
										</div>
									))}
								</div>
							</div>
						) : coinStats ? (
							<div className="space-y-4 mt-6 flex-1 text-center">
								{/* 24h stats */}
								<div>
									<div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
										<div className="text-gray-500 text-right">24H LOW:</div>
										<div className="font-medium text-left">
											{coinStats.low24h != null
												? formatPrice(coinStats.low24h)
												: "—"}
										</div>
										<div className="text-gray-500 text-right">24H HIGH:</div>
										<div className="font-medium text-left">
											{coinStats.high24h != null
												? formatPrice(coinStats.high24h)
												: "—"}
										</div>
										<div className="text-gray-500 text-right">24H VOLUME:</div>
										<div className="font-medium text-left">
											{coinStats.volume24h != null
												? formatNumber(coinStats.volume24h)
												: "—"}
										</div>
									</div>
								</div>

								{/* 52w stats */}
								<div>
									<div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
										<div className="text-gray-500 text-right">52W LOW:</div>
										<div className="font-medium text-left">
											{coinStats.low52w != null
												? formatPrice(coinStats.low52w)
												: "—"}
										</div>
										<div className="text-gray-500 text-right">52W HIGH:</div>
										<div className="font-medium text-left">
											{coinStats.high52w != null
												? formatPrice(coinStats.high52w)
												: "—"}
										</div>
									</div>
								</div>

								{/* open/close stats */}
								<div className="pt-2 border-t border-gray-200">
									<div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
										<div className="text-gray-500 text-right">OPEN:</div>
										<div className="font-medium text-left">
											{coinStats.open != null
												? formatPrice(coinStats.open)
												: "—"}
										</div>
										<div className="text-gray-500 text-right">CURRENT:</div>
										<div className="font-medium text-left">
											{coinStats.close != null
												? formatPrice(coinStats.close)
												: "—"}
										</div>
									</div>
								</div>
							</div>
						) : (
							<p className="text-gray-500 mt-6 text-center">
								No stats available
							</p>
						)}
					</div>
				</div>

				{/* chart */}
				<div className="flex-1 flex flex-col">
					<div className="flex items-center justify-between mb-4">
						<div className="flex items-center gap-2">
							<button
								onClick={() => setChartType("line")}
								className={`p-2 rounded border ${
									chartType === "line"
										? "bg-gray-100 border-gray-400"
										: "border-gray-300 hover:cursor-pointer"
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
								>
									<polyline points="22,6 12,13 7,9 2,15" />
								</svg>
							</button>
							<button
								onClick={() => {
									setChartType("candle");
									if (period === "7D") setPeriod("1M");
								}}
								className={`p-2 rounded border ${
									chartType === "candle"
										? "bg-gray-100 border-gray-400"
										: "border-gray-300 hover:cursor-pointer"
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
								>
									<line x1="6" y1="4" x2="6" y2="20" />
									<rect x="4" y="8" width="4" height="8" fill="currentColor" />
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
									onClick={() => setPeriod(p)}
									className={`px-3 py-1 text-sm rounded-lg border border-gray-200 ${
										period === p
											? "bg-gray-100 border-gray-400"
											: "text-gray-600 hover:bg-gray-100 hover:cursor-pointer"
									}`}
								>
									{p}
								</button>
							))}
						</div>
					</div>

					<div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 flex-1">
						{chartLoading ? (
							<div className="h-80 flex items-center justify-center">
								<span className="text-gray-500">Loading chart...</span>
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
												formatPrice(value),
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
			</div>
		</div>
	);
};

export default CoinPage;

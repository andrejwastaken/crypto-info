import { useEffect, useState } from "react";
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

const CoinPage = () => {
	const { symbol } = useParams<{ symbol: string }>();
	const [coinData, setCoinData] = useState<OhlcvData[]>([]);
	const [coinStats, setCoinStats] = useState<CoinStats | null>(null);
	const [period, setPeriod] = useState<TimePeriod>("1Y");
	const [chartType, setChartType] = useState<ChartType>("line");
	const [chartLoading, setChartLoading] = useState(true);
	const [statsLoading, setStatsLoading] = useState(true);

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
					{statsLoading ? (
						<div className="animate-pulse space-y-4">
							<div className="h-6 w-32 bg-gray-200 rounded"></div>
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
						<div className="space-y-4 mt-15">
							{/* 24h stats */}
							<div>
								<div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
									<div className="text-gray-500">24H LOW:</div>
									<div className="font-medium">
										{coinStats.low24h != null
											? formatPrice(coinStats.low24h)
											: "—"}
									</div>
									<div className="text-gray-500">24H HIGH:</div>
									<div className="font-medium">
										{coinStats.high24h != null
											? formatPrice(coinStats.high24h)
											: "—"}
									</div>
									<div className="text-gray-500">24H VOLUME:</div>
									<div className="font-medium">
										{coinStats.volume24h != null
											? formatNumber(coinStats.volume24h)
											: "—"}
									</div>
								</div>
							</div>

							{/* 52w stats */}
							<div>
								<div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
									<div className="text-gray-500">52W LOW:</div>
									<div className="font-medium">
										{coinStats.low52w != null
											? formatPrice(coinStats.low52w)
											: "—"}
									</div>
									<div className="text-gray-500">52W HIGH:</div>
									<div className="font-medium">
										{coinStats.high52w != null
											? formatPrice(coinStats.high52w)
											: "—"}
									</div>
								</div>
							</div>

							{/* open/close stats */}
							<div className="pt-2 border-t border-gray-200">
								<div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
									<div className="text-gray-500">OPEN:</div>
									<div className="font-medium">
										{coinStats.open != null ? formatPrice(coinStats.open) : "—"}
									</div>
									<div className="text-gray-500">CURRENT:</div>
									<div className="font-medium">
										{coinStats.close != null
											? formatPrice(coinStats.close)
											: "—"}
									</div>
								</div>
							</div>
						</div>
					) : (
						<p className="text-gray-500">No stats available</p>
					)}
				</div>

				{/* chart */}
				<div className="flex-1">
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
									className={`px-3 py-1 text-sm rounded ${
										period === p
											? "bg-gray-800 text-white"
											: "text-gray-600 hover:bg-gray-100 hover:cursor-pointer"
									}`}
								>
									{p}
								</button>
							))}
						</div>
					</div>

					<div className="bg-white rounded-lg border border-gray-200 p-4">
						{chartLoading ? (
							<div className="h-80 flex items-center justify-center">
								<span className="text-gray-500">Loading chart...</span>
							</div>
						) : (
							<ResponsiveContainer width="100%" height={320}>
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

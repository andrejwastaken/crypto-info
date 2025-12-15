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
import NewsSection from "../components/NewsSection";
import { formatNumber, formatPrice } from "../helpers";
import type { CoinStats, OhlcvData } from "../types";

type TimePeriod = "7D" | "1M" | "3M" | "1Y" | "Max";
type ChartType = "line" | "candle";
type AnalysisTimePeriod = "DAY" | "WEEK" | "MONTH";

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
		showTick: false,
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
		showTick: false,
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

	const [taScores, setTaScores] = useState<
		Record<AnalysisTimePeriod, number | null>
	>({
		DAY: null,
		WEEK: null,
		MONTH: null,
	});
	const [taPeriod, setTaPeriod] = useState<AnalysisTimePeriod>("DAY");
	const [taLoading, setTaLoading] = useState(false);
	const [prediction, setPrediction] = useState<{
		price: number;
	} | null>(null);

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

	const fetchTechnicalAnalysis = async (periodToFetch: AnalysisTimePeriod) => {
		if (!symbol) return;

		setTaPeriod(periodToFetch);
		if (taScores[periodToFetch] !== null) return;

		setTaLoading(true);
		try {
			const res = await fetch(
				`http://localhost:8080/api/ta/${symbol}?period=${periodToFetch}`
			);
			if (res.ok) {
				const data = await res.json();
				const score = data;
				setTaScores((prev) => ({ ...prev, [periodToFetch]: score }));
			}
		} catch (error) {
			console.error("Failed to fetch TA:", error);
		} finally {
			setTaLoading(false);
		}
	};

	useEffect(() => {
		fetchTechnicalAnalysis("DAY");
	}, [symbol]);

	useEffect(() => {
		const fetchPrediction = async () => {
			if (!symbol) return;

			try {
				const res = await fetch(
					`http://localhost:8080/api/prediction/${symbol}`
				);
				if (res.ok) {
					const data = await res.json();
					setPrediction({
						price: data.predictedClose,
					});
				} else if (res.status === 404) {
					setPrediction(null);
				}
			} catch (error) {
				console.error("Failed to fetch prediction:", error);
				setPrediction(null);
			}
		};

		fetchPrediction();
	}, [symbol]);

	useEffect(() => {
		if (typeof window !== "undefined") {
			window.scrollTo({ top: 0, left: 0, behavior: "auto" });
		}
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
						<h1 className="text-3xl font-semibold text-gray-800 mb-2">
							{coinName} ({symbol})
						</h1>
						{coinStats && (
							<div className="flex items-baseline gap-3">
								<span className="text-4xl font-bold text-gray-900">
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

						<div className="flex justify-center gap-2 mb-4">
							{(["DAY", "WEEK", "MONTH"] as AnalysisTimePeriod[]).map((p) => (
								<button
									key={p}
									onClick={() => fetchTechnicalAnalysis(p)}
									className={`px-3 py-1 text-xs rounded-lg border border-gray-200 ${
										taPeriod === p
											? "bg-gray-100 border-gray-400 font-medium"
											: "text-gray-600 hover:bg-gray-100 hover:cursor-pointer"
									}`}
								>
									{p === "DAY" ? "1D" : p === "WEEK" ? "1W" : "1M"}
								</button>
							))}
						</div>

						{taLoading ? (
							<div className="h-40 flex items-center justify-center">
								<span className="text-gray-400 text-sm">
									Loading analysis...
								</span>
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
												// tooltip: {
												// 	text: zone.label,
												// },
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
								<div className="flex items-center justify-center gap-1 mt-2 text-xs text-gray-400">
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
										<div className="hidden group-hover/tooltip:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-gray-800 text-white rounded text-[10px] z-10 shadow-lg text-center">
											The signal score is calculated using oscilator and moving
											average metrics over the specified period. For more
											details, visit the{" "}
											<span className="font-bold">How it works?</span> page.
										</div>
									</div>
								</div>
							</>
						)}

						<div className="mt-6 p-4 bg-linear-to-br from-indigo-50 to-blue-50 rounded-xl border border-indigo-100 shadow-sm relative overflow-visible">
							<h4 className="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-2 text-center">
								Tomorrow's Prediction
							</h4>
							{/* todo: != 0.00 is a temp fix, make changes in the script and in the db*/}
							{prediction &&
							coinStats &&
							coinStats.close &&
							prediction.price != 0.0 &&
							prediction.price != 1.0 ? (
								<div className="flex flex-col items-center justify-center">
									<span className="text-2xl font-bold text-gray-900">
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
										<div className="group/tooltip relative flex items-center text-gray-400">
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
											<div className="hidden group-hover/tooltip:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-gray-800 text-white rounded text-[10px] z-10 shadow-lg text-center">
												This prediction is made using an LSTM model. For more
												details, go to the `XXXXX` page.
											</div>
										</div>
									</span>
								</div>
							) : (
								<div className="flex items-center justify-center py-2">
									<span className="text-sm text-gray-500">
										No prediction available
									</span>
								</div>
							)}
						</div>

						<p className="mt-6 text-xs text-center text-gray-500 italic">
							This is not financial advice
						</p>
					</div>
				</div>

				{/* chart */}
				<div className="flex-1 flex flex-col">
					<div className="flex items-center justify-between mb-4">
						<div className="flex items-center gap-2">
							<button
								onClick={() => setChartType("line")}
								className={`p-2 rounded-lg border border-gray-200 ${
									chartType === "line"
										? "bg-gray-100 border-gray-400"
										: "text-gray-600 hover:bg-gray-100 hover:cursor-pointer"
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
								className={`p-2 rounded-lg border border-gray-200 ${
									chartType === "candle"
										? "bg-gray-100 border-gray-400"
										: "text-gray-600 hover:bg-gray-100 hover:cursor-pointer"
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

			{/* historic stats below the chart */}
			{statsLoading ? (
				<div className="mt-6 bg-white rounded-lg border border-gray-200 shadow-sm p-6">
					<div className="animate-pulse space-y-4">
						<div className="h-6 w-32 bg-gray-200 rounded mx-auto"></div>
						<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
							{[...Array(3)].map((_, i) => (
								<div key={i} className="space-y-2">
									{[...Array(3)].map((_, j) => (
										<div key={j} className="flex justify-between">
											<div className="h-4 w-20 bg-gray-200 rounded"></div>
											<div className="h-4 w-24 bg-gray-200 rounded"></div>
										</div>
									))}
								</div>
							))}
						</div>
					</div>
				</div>
			) : coinStats ? (
				<div className="mt-6 bg-white rounded-lg border border-gray-200 shadow-sm p-6">
					<h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
						Historic Statistics
					</h3>
					<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
						{/* 24h stats */}
						<div className="text-center">
							<h4 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wider">
								24 Hour
							</h4>
							<div className="space-y-2 text-sm">
								<div className="flex justify-between">
									<span className="text-gray-500">Low:</span>
									<span className="font-medium">
										{coinStats.low24h != null
											? formatPrice(coinStats.low24h)
											: "—"}
									</span>
								</div>
								<div className="flex justify-between">
									<span className="text-gray-500">High:</span>
									<span className="font-medium">
										{coinStats.high24h != null
											? formatPrice(coinStats.high24h)
											: "—"}
									</span>
								</div>
								<div className="flex justify-between">
									<span className="text-gray-500">Volume:</span>
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
							<h4 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wider">
								52 Week
							</h4>
							<div className="space-y-2 text-sm">
								<div className="flex justify-between">
									<span className="text-gray-500">Low:</span>
									<span className="font-medium">
										{coinStats.low52w != null
											? formatPrice(coinStats.low52w)
											: "—"}
									</span>
								</div>
								<div className="flex justify-between">
									<span className="text-gray-500">High:</span>
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
							<h4 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wider">
								Price Points
							</h4>
							<div className="space-y-2 text-sm">
								<div className="flex justify-between">
									<span className="text-gray-500">Open:</span>
									<span className="font-medium">
										{coinStats.open != null ? formatPrice(coinStats.open) : "—"}
									</span>
								</div>
								<div className="flex justify-between">
									<span className="text-gray-500">Current:</span>
									<span className="font-medium">
										{coinStats.close != null
											? formatPrice(coinStats.close)
											: "—"}
									</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			) : null}

			<NewsSection symbol={symbol} />
		</div>
	);
};

export default CoinPage;

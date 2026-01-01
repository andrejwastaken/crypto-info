import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import HistoricStats from "../components/HistoricStats";
import NewsSection from "../components/NewsSection";
import PriceChart from "../components/PriceChart";
import TechnicalAnalysisGauge from "../components/TechnicalAnalysisGauge";
import TechnicalAnalysisIndicators from "../components/TechnicalAnalysisIndicators";
import { periodToSize } from "../constants/coinPageConstants";
import { API_BASE_URL } from "../consts";
import { formatPrice } from "../helpers";
import type {
	AnalysisTimePeriod,
	ChartType,
	CoinStats,
	OhlcvData,
	PredictionData,
	TechnicalAnalysisStats,
	TimePeriod,
} from "../types";

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
	const [prediction, setPrediction] = useState<PredictionData | null>(null);

	const [taStats, setTaStats] = useState<
		Record<AnalysisTimePeriod, TechnicalAnalysisStats | null>
	>({
		DAY: null,
		WEEK: null,
		MONTH: null,
	});
	const [taStatsPeriod, setTaStatsPeriod] = useState<AnalysisTimePeriod>("DAY");
	const [taStatsLoading, setTaStatsLoading] = useState(false);

	// fetch stats only once on initial load
	useEffect(() => {
		const fetchStats = async () => {
			if (!symbol) return;
			setStatsLoading(true);

			try {
				const res = await fetch(
					`${API_BASE_URL}/api/ohlcv-data/${symbol}/stats`
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
				`${API_BASE_URL}/api/ta/${symbol}/score?period=${periodToFetch}`
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

	const fetchTechnicalAnalysisStats = async () => {
		if (!symbol) return;

		setTaStatsLoading(true);
		try {
			const res = await fetch(`${API_BASE_URL}/api/ta/${symbol}`);
			if (res.ok) {
				const data = await res.json();
				// data is an array with 3 items, one for each period
				const newStats = { DAY: null, WEEK: null, MONTH: null } as Record<
					AnalysisTimePeriod,
					any
				>;

				data.forEach((item: any) => {
					if (
						item.period === "DAY" ||
						item.period === "WEEK" ||
						item.period === "MONTH"
					) {
						newStats[item.period as AnalysisTimePeriod] = item;
					}
				});

				setTaStats(newStats);
			}
		} catch (error) {
			console.error("Failed to fetch TA stats:", error);
		} finally {
			setTaStatsLoading(false);
		}
	};

	useEffect(() => {
		fetchTechnicalAnalysisStats();
	}, [symbol]);

	useEffect(() => {
		const fetchPrediction = async () => {
			if (!symbol) return;

			try {
				const res = await fetch(`${API_BASE_URL}/api/prediction/${symbol}`);
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
					`${API_BASE_URL}/api/ohlcv-data/${symbol}${sizeParam}`
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
		<div className="min-h-screen bg-slate-800">
			<div className="container mx-auto px-4 py-8">
				<div className="mb-6">
					{statsLoading ? (
						<div className="animate-pulse">
							<div className="h-8 w-64 bg-slate-600 rounded mb-2"></div>
							<div className="h-10 w-48 bg-slate-600 rounded"></div>
						</div>
					) : (
						<>
							<h1 className="text-3xl font-semibold text-amber-100 mb-2">
								{coinName} ({symbol})
							</h1>
							{coinStats && (
								<div className="flex items-baseline gap-3">
									<span className="text-4xl font-bold text-amber-50">
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
					<TechnicalAnalysisGauge
						taScores={taScores}
						taPeriod={taPeriod}
						taLoading={taLoading}
						prediction={prediction}
						coinStats={coinStats}
						onPeriodChange={fetchTechnicalAnalysis}
					/>
					<PriceChart
						chartData={chartData}
						mergedCandleData={mergedCandleData}
						chartType={chartType}
						period={period}
						priceChange={priceChange}
						chartLoading={chartLoading}
						onChartTypeChange={setChartType}
						onPeriodChange={setPeriod}
					/>
				</div>

				<HistoricStats coinStats={coinStats} statsLoading={statsLoading} />

				<TechnicalAnalysisIndicators
					taStats={taStats}
					taStatsPeriod={taStatsPeriod}
					taStatsLoading={taStatsLoading}
					onPeriodChange={setTaStatsPeriod}
				/>

				<NewsSection symbol={symbol} />
			</div>
		</div>
	);
};

export default CoinPage;

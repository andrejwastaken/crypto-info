export type OhlcvData = {
	id: number;
	close: number;
	date: string;
	high: number;
	low: number;
	name: string;
	open: number;
	symbol: string;
	volume: number;
};

export type Coin = {
	id: number;
	symbol: string;
	name: string;
	updatedAt: string | null;
	marketCap: number | null;
	circulatingSupply: number | null;
	volume: number | null;
	change52w: number | null;
};

export type CoinStats = {
	low24h: number | null;
	high24h: number | null;
	volume24h: number | null;
	open: number | null;
	close: number | null;
	low52w: number | null;
	high52w: number | null;
	symbol: string;
	name: string;
};

export type CoinCarousel = {
	pctChange: number;
	symbol: string;
};

// LandingPage types
export type SortField =
	| "name"
	| "marketCap"
	| "volume"
	| "circulatingSupply"
	| "change52w";

export type Prediction = {
	symbol: string;
	predictedClose: number;
	predictedChangePct: number;
};

export type PredictionsData = {
	top: Prediction[];
	bottom: Prediction[];
};

export type ChainSentimentPrediction = {
	id: number;
	symbol: string;
	date: string;
	predictedClose: number;
	predictedChangePct: number;
};

export type OnChainMetric = {
	id: number;
	symbol: string;
	date: string;
	activeAddresses: number;
	transactions: number;
	exchangeInflow: number;
	exchangeOutflow: number;
	whaleTransactions: number;
	nvtRatio: number;
	mvrvRatio: number;
	netFlow: number;
	securityValue: number;
	tvlUsd: number;
};

// CoinPage types
export type TimePeriod = "7D" | "1M" | "3M" | "1Y" | "Max";
export type ChartType = "line" | "candle";
export type AnalysisTimePeriod = "DAY" | "WEEK" | "MONTH";

export type TechnicalAnalysisStats = {
	date: string;
	rsi: number;
	macdLine: number;
	macdSignal: number;
	stochK: number;
	stochD: number;
	dmiPlus: number;
	dmiMinus: number;
	adx: number;
	cci: number;
	sma: number;
	ema: number;
	wma: number;
	bollingerMiddle: number;
	volumeSma: number;
	normalizedScore: number;
};

export type PredictionData = {
	price: number;
};

export type MergedCandleData = {
	date: string;
	dateRange: string;
	open: number;
	high: number;
	low: number;
	close: number;
	openClose: [number, number];
	highLow: [number, number];
	isUp: boolean;
};

// base types

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

// NewsSection types
export interface NewsArticle {
	id: number;
	title: string;
	img_src: string;
	symbols: string[];
	link: string;
	date: string;
	sentiment: "Positive" | "Negative" | "Neutral";
	score: number;
}

// API response types

// CoinController
export type CoinListResponse = Coin[];

// OhlcvDataController
export type OhlcvDataPagedResponse = {
	_embedded: {
		ohlcvDataList: OhlcvData[];
	};
	_links: {
		first?: { href: string };
		self: { href: string };
		next?: { href: string };
		last?: { href: string };
	};
	page: {
		size: number;
		totalElements: number;
		totalPages: number;
		number: number;
	};
};

export type CoinStatsResponse = CoinStats;

export type CarouselDataResponse = CoinCarousel[];

// OhlcvPredictionController
export type PredictionResponse = {
	id: number;
	symbol: string;
	date: string;
	predictedClose: number;
	predictedChangePct: number;
};

export type ExtremesResponse = {
	top: PredictionResponse[];
	bottom: PredictionResponse[];
};

// TechnicalAnalysisController
export type TechnicalAnalysisScoreResponse = number;

export type TechnicalAnalysisDataResponse = {
	id: number;
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
	symbol: string;
	sma: number;
	ema: number;
	wma: number;
	bollingerMiddle: number;
	volumeSma: number;
	normalizedScore: number;
	period: AnalysisTimePeriod;
}[];

// OnChainMetricController
export type OnChainMetricListResponse = OnChainMetric[];

// OnChainSentimentPredictionController
export type ChainSentimentPredictionListResponse = ChainSentimentPrediction[];

// TextSentimentController
export type TextSentimentPagedResponse = {
	_embedded: {
		textSentimentList: Array<{
			id: number;
			title: string;
			date: string;
			symbols: string[];
			link: string;
			imageLink: string;
			label: string;
			score: number;
		}>;
	};
	_links: {
		first?: { href: string };
		self: { href: string };
		next?: { href: string };
		last?: { href: string };
	};
	page: {
		size: number;
		totalElements: number;
		totalPages: number;
		number: number;
	};
};

export type SentimentUpdateStatusResponse =
	| {
			status: "idle";
			lastCompletedAt?: string;
			minutesUntilNextUpdate: number;
	  }
	| {
			status: "running" | "pending";
			startedAt: string;
	  }
	| {
			status: "failed";
			message: string;
	  };

export type SentimentUpdateTriggerResponse =
	| {
			accepted: true;
	  }
	| {
			message: string;
			minutesUntilNextUpdate: number;
	  };

// context types

export type CoinsContextType = {
	coins: Coin[];
	coinsCarousel: CoinCarousel[];
	loading: boolean;
};

export type NewsUpdateContextType = {
	isUpdateAvailable: boolean;
	updateButtonText: string;
	minutesRemaining: number | null;
	triggerUpdate: () => Promise<void>;
	isPolling: boolean;
};

export type NewsUpdateStoredState = {
	nextAvailableTime: number | null;
	isUpdateAvailable: boolean;
	isPolling?: boolean;
	pollingStartTime?: number;
};

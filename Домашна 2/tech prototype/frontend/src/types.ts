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

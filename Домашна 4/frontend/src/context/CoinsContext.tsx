import {
	createContext,
	useContext,
	useEffect,
	useState,
	type ReactNode,
} from "react";
import { API_BASE_URL } from "../consts";
import type {
	CarouselDataResponse,
	Coin,
	CoinCarousel,
	CoinListResponse,
	CoinsContextType,
} from "../types";

const CoinsContext = createContext<CoinsContextType>({
	coins: [],
	coinsCarousel: [],
	loading: true,
});

export const useCoins = () => useContext(CoinsContext);

export const CoinsProvider = ({ children }: { children: ReactNode }) => {
	const [coins, setCoins] = useState<Coin[]>([]);
	const [coinsCarousel, setCoinsCarousel] = useState<CoinCarousel[]>([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchCoins = async () => {
			try {
				const res = await fetch(`${API_BASE_URL}/api/coins/`);
				const data: CoinListResponse = await res.json();
				const coinList: Coin[] = data || [];
				setCoins(coinList);
			} catch (error) {
				console.error("Failed to fetch coins:", error);
			} finally {
				setLoading(false);
			}
		};

		const fetchCarouselCoins = async () => {
			try {
				const res = await fetch(`${API_BASE_URL}/api/ohlcv-data/carousel`);
				const data: CarouselDataResponse = await res.json();
				const coinList: CoinCarousel[] = data || [];
				setCoinsCarousel(coinList);
			} catch (error) {
				console.error("Failed to fetch carousel data:", error);
			} finally {
			}
		};

		fetchCoins();
		fetchCarouselCoins();
	}, []);

	return (
		<CoinsContext.Provider value={{ coins, loading, coinsCarousel }}>
			{children}
		</CoinsContext.Provider>
	);
};

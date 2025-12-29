import {
	createContext,
	useContext,
	useEffect,
	useState,
	type ReactNode,
} from "react";
import type { Coin, CoinCarousel } from "../types";

type CoinsContextType = {
	coins: Coin[];
	coinsCarousel: CoinCarousel[];
	loading: boolean;
};

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
				const res = await fetch("http://localhost:8080/api/coins/");
				const data = await res.json();
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
				const res = await fetch(
					"http://localhost:8080/api/ohlcv-data/carousel"
				);
				const data = await res.json();
				const coinList: CoinCarousel[] = data || [];
				console.log(coinList);
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

import {
	createContext,
	useContext,
	useEffect,
	useState,
	type ReactNode,
} from "react";
import type { Coin } from "../types";

type CoinsContextType = {
	coins: Coin[];
	loading: boolean;
};

const CoinsContext = createContext<CoinsContextType>({
	coins: [],
	loading: true,
});

export const useCoins = () => useContext(CoinsContext);

export const CoinsProvider = ({ children }: { children: ReactNode }) => {
	const [coins, setCoins] = useState<Coin[]>([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchCoins = async () => {
			try {
				const res = await fetch("http://localhost:8080/api/coins/");
				const data = await res.json();
				console.log(data);
				const coinList: Coin[] = data || [];
				setCoins(coinList);
			} catch (error) {
				console.error("Failed to fetch coins:", error);
			} finally {
				setLoading(false);
			}
		};

		fetchCoins();
	}, []);

	return (
		<CoinsContext.Provider value={{ coins, loading }}>
			{children}
		</CoinsContext.Provider>
	);
};

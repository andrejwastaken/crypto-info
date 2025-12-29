import { useCoins } from "../context/CoinsContext";

const CryptoTicker = () => {
	const { coinsCarousel } = useCoins();

	return (
		<div className="w-full overflow-hidden bg-amber-200 py-2">
			<style>{`
                @keyframes ticker-scroll {
                    0% { transform: translateX(0); }
                    100% { transform: translateX(-50%); }
                }
                .animate-ticker {
                    display: flex;
                    width: max-content;
                    animation: ticker-scroll 30s linear infinite;
                }
                .animate-ticker:hover {
                    animation-play-state: paused;
                }
            `}</style>

			<div className="animate-ticker flex gap-12 px-4">
				{coinsCarousel != null &&
					coinsCarousel.map((coin, index) => (
						<div
							key={`${coin.symbol}-${index}`}
							className="flex items-center gap-2 text-sm font-medium"
						>
							<span className="text-slate-700">{coin.symbol}</span>
							<span
								className={
									coin.pctChange >= 0 ? "text-green-600" : "text-red-600"
								}
							>
								{coin.pctChange > 0 ? "+" : ""}
								{coin.pctChange.toFixed(2)}%
							</span>
						</div>
					))}
			</div>
		</div>
	);
};

export default CryptoTicker;

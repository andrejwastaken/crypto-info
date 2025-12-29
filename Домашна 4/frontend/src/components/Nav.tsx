import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCoins } from "../context/CoinsContext";
import CryptoTicker from "./CryptoTicker";

const Nav = () => {
	const { coins } = useCoins();
	const navigate = useNavigate();
	const [searchQuery, setSearchQuery] = useState("");
	const [showSuggestions, setShowSuggestions] = useState(false);
	const [selectedIndex, setSelectedIndex] = useState(-1);
	const SEARCH_RESULTS = 3;

	const filteredCoins = searchQuery.trim()
		? coins
				.filter(
					(coin) =>
						coin.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
						coin.name.toLowerCase().includes(searchQuery.toLowerCase())
				)
				.sort((a, b) => (b.marketCap ?? 0) - (a.marketCap ?? 0))
				.slice(0, SEARCH_RESULTS)
		: [];

	const handleSelect = (symbol: string) => {
		setSearchQuery("");
		setShowSuggestions(false);
		setSelectedIndex(-1);
		navigate(`/coins/${symbol}`);
	};

	const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (!showSuggestions || filteredCoins.length === 0) return;

		switch (e.key) {
			case "ArrowDown":
				e.preventDefault();
				setSelectedIndex((prev) =>
					prev < filteredCoins.length - 1 ? prev + 1 : prev
				);
				break;
			case "ArrowUp":
				e.preventDefault();
				setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
				break;
			case "Enter":
				e.preventDefault();
				if (selectedIndex >= 0 && selectedIndex < filteredCoins.length) {
					handleSelect(filteredCoins[selectedIndex].symbol);
				}
				break;
			case "Escape":
				setShowSuggestions(false);
				setSelectedIndex(-1);
				break;
		}
	};

	const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setSearchQuery(e.target.value);
		setSelectedIndex(-1);
	};

	return (
		<div className="flex flex-col w-full shadow-sm">
			<nav className="bg-amber-100 flex items-center justify-between px-8 py-2 z-20 relative">
				<div className="flex items-center gap-4">
					<Link to="/">
						<img src="/logo.png" width={90} alt="Logo" />
					</Link>
					<div className="relative">
						<input
							type="text"
							placeholder="Search for symbols"
							value={searchQuery}
							onChange={handleSearchChange}
							onKeyDown={handleKeyDown}
							onFocus={() => setShowSuggestions(true)}
							onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
							className="pl-4 sm:pr-30 lg:pr-100 py-2 rounded-full bg-white border border-slate-300 
                            focus:outline-none focus:ring-2 focus:ring-slate-400 min-w-[150px] mr-1"
						/>
						<span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
							<svg width="18" height="18" fill="none" viewBox="0 0 24 24">
								<path
									stroke="currentColor"
									strokeWidth="2"
									strokeLinecap="round"
									strokeLinejoin="round"
									d="M21 21l-4.35-4.35M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16z"
								/>
							</svg>
						</span>
						{showSuggestions && filteredCoins.length > 0 && (
							<div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-300 rounded-lg shadow-lg z-50 overflow-hidden">
								{filteredCoins.map((coin, index) => (
									<div
										key={coin.id}
										onClick={() => handleSelect(coin.symbol)}
										className={`px-4 py-2 cursor-pointer flex justify-between items-center ${
											index === selectedIndex
												? "bg-slate-200"
												: "hover:bg-slate-100"
										}`}
									>
										<span className="font-medium">{coin.symbol}</span>
										<span className="text-sm text-slate-500">{coin.name}</span>
									</div>
								))}
							</div>
						)}
					</div>
				</div>
				<div className="flex items-center gap-5 xl:gap-30 text-slate-900 font-medium">
					<Link to="/" className="hover:underline">
						Home
					</Link>
					<Link to="/how-it-works" className="hover:underline">
						How it works?
					</Link>
					<Link to="/about" className="hover:underline">
						About us
					</Link>
				</div>
			</nav>

			<CryptoTicker />
		</div>
	);
};

export default Nav;

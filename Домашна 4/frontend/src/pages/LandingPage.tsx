import { useEffect, useMemo, useState } from "react";
import CryptoTable from "../components/CryptoTable";
import OnChainMetricsCard from "../components/OnChainMetricsCard";
import PredictionsCard from "../components/PredictionsCard";
import Spinner from "../components/Spinner";
import { API_BASE_URL } from "../consts";
import { useCoins } from "../context/CoinsContext";
import type {
	ChainSentimentPrediction,
	OnChainMetric,
	PredictionsData,
	SortField,
} from "../types";

const LandingPage = () => {
	const { coins, loading } = useCoins();
	const [pageSize, setPageSize] = useState(25);
	const [currentPage, setCurrentPage] = useState(0);
	const [sortBy, setSortBy] = useState<SortField>("marketCap");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
	const [predictions, setPredictions] = useState<PredictionsData | null>(null);
	const [predictionsLoading, setPredictionsLoading] = useState(true);
	const [chainSentimentPredictions, setChainSentimentPredictions] = useState<
		ChainSentimentPrediction[]
	>([]);
	const [chainSentimentLoading, setChainSentimentLoading] = useState(true);
	const [onChainMetrics, setOnChainMetrics] = useState<OnChainMetric[]>([]);
	const [onChainLoading, setOnChainLoading] = useState(true);

	useEffect(() => {
		const fetchPredictions = async () => {
			try {
				const response = await fetch(`${API_BASE_URL}/api/prediction/extremes`);
				if (response.ok) {
					const data = await response.json();
					setPredictions(data);
				}
			} catch (error) {
				console.error("Failed to fetch predictions:", error);
			} finally {
				setPredictionsLoading(false);
			}
		};

		const fetchChainSentimentPredictions = async () => {
			try {
				const response = await fetch(
					`${API_BASE_URL}/api/chain-sentiment-prediction`
				);
				if (response.ok) {
					const data = await response.json();
					setChainSentimentPredictions(data);
				}
			} catch (error) {
				console.error("Failed to fetch chain-sentiment predictions:", error);
			} finally {
				setChainSentimentLoading(false);
			}
		};

		const fetchOnChainMetrics = async () => {
			try {
				const response = await fetch(`${API_BASE_URL}/api/on-chain`);
				if (response.ok) {
					const data = await response.json();
					setOnChainMetrics(data);
				}
			} catch (error) {
				console.error("Failed to fetch on-chain metrics:", error);
			} finally {
				setOnChainLoading(false);
			}
		};

		fetchPredictions();
		fetchChainSentimentPredictions();
		fetchOnChainMetrics();
	}, []);

	const sortedCoins = useMemo(() => {
		return [...coins].sort((a, b) => {
			if (sortBy === "name") {
				const aName = a.name?.toLowerCase() ?? "";
				const bName = b.name?.toLowerCase() ?? "";
				const result = aName.localeCompare(bName);
				return sortOrder === "desc" ? -result : result;
			}

			const aVal = a[sortBy] ?? 0;
			const bVal = b[sortBy] ?? 0;
			return sortOrder === "desc" ? bVal - aVal : aVal - bVal;
		});
	}, [coins, sortBy, sortOrder]);

	const handlePageSizeChange = (newSize: number) => {
		setPageSize(newSize);
		setCurrentPage(0);
	};

	if (loading) {
		return (
			<div className="min-h-screen bg-slate-800">
				<div className="container mx-auto px-4 py-8 flex items-center justify-center">
					<Spinner size="lg" color="amber" />
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-slate-800">
			<div className="container mx-auto px-4 py-8">
				{/* predictions and on-chain metrics section */}
				<div className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
					<PredictionsCard
						predictions={predictions}
						predictionsLoading={predictionsLoading}
						chainSentimentPredictions={chainSentimentPredictions}
						chainSentimentLoading={chainSentimentLoading}
					/>
					<OnChainMetricsCard
						onChainMetrics={onChainMetrics}
						onChainLoading={onChainLoading}
					/>
				</div>

				<CryptoTable
					sortedCoins={sortedCoins}
					pageSize={pageSize}
					currentPage={currentPage}
					sortBy={sortBy}
					sortOrder={sortOrder}
					onPageSizeChange={handlePageSizeChange}
					onSortByChange={setSortBy}
					onSortOrderChange={setSortOrder}
					onPageChange={setCurrentPage}
				/>
			</div>
		</div>
	);
};

export default LandingPage;

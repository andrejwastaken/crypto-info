import type { ReactNode } from "react";
import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useRef,
	useState,
} from "react";
import { API_BASE_URL } from "../consts";

interface NewsUpdateContextType {
	isUpdateAvailable: boolean;
	updateButtonText: string;
	minutesRemaining: number | null;
	triggerUpdate: () => Promise<void>;
	isPolling: boolean;
}

const NewsUpdateContext = createContext<NewsUpdateContextType | undefined>(
	undefined
);

const STORAGE_KEY = "newsUpdateState";

interface StoredState {
	nextAvailableTime: number | null;
	isUpdateAvailable: boolean;
	isPolling?: boolean;
	pollingStartTime?: number;
}

const getLatestNewsText = (
	state: "DEFAULT" | "LOADING" | "UNAVAILABLE",
	mins?: number
): string => {
	switch (state) {
		case "DEFAULT":
			return "Update latest news";
		case "LOADING":
			return "Currently updating latest news...";
		case "UNAVAILABLE":
			return `Updated recently. Try in ${mins} minute${mins !== 1 ? "s" : ""}.`;
	}
};

export const NewsUpdateProvider = ({ children }: { children: ReactNode }) => {
	const [isUpdateAvailable, setIsUpdateAvailable] = useState(true);
	const [updateButtonText, setUpdateButtonText] =
		useState("Update latest news");
	const [nextAvailableTime, setNextAvailableTime] = useState<number | null>(
		null
	);
	const [minutesRemaining, setMinutesRemaining] = useState<number | null>(null);
	const [isPolling, setIsPolling] = useState(false);

	// Refs to track intervals and timeouts for cleanup
	const pollIntervalRef = useRef<number | null>(null);
	const pollingStartTimeRef = useRef<number | null>(null);

	// Cleanup function for polling
	const cleanupPolling = useCallback(() => {
		if (pollIntervalRef.current) {
			clearInterval(pollIntervalRef.current);
			pollIntervalRef.current = null;
		}
		pollingStartTimeRef.current = null;
		setIsPolling(false);
	}, []);

	// Polling logic
	const startPolling = useCallback(() => {
		const POLLING_TIMEOUT = 2 * 60 * 1000; // 2 minutes

		pollIntervalRef.current = setInterval(async () => {
			if (
				pollingStartTimeRef.current &&
				Date.now() - pollingStartTimeRef.current > POLLING_TIMEOUT
			) {
				cleanupPolling();
				setIsUpdateAvailable(true);
				setUpdateButtonText(getLatestNewsText("DEFAULT"));
				localStorage.removeItem(STORAGE_KEY);
				window.dispatchEvent(new CustomEvent("newsUpdateFailed"));
				return;
			}

			try {
				const response = await fetch(`${API_BASE_URL}/api/sentiment/status`);
				const data = await response.json();

				if (data.status === "idle") {
					cleanupPolling();

					const minutesUntilNext = data.minutesUntilNextUpdate;
					const nextAvailable = Date.now() + minutesUntilNext * 60 * 1000;
					setNextAvailableTime(nextAvailable);

					setIsUpdateAvailable(false);
					setUpdateButtonText(
						getLatestNewsText("UNAVAILABLE", minutesUntilNext)
					);

					// Dispatch custom event to notify components
					window.dispatchEvent(new CustomEvent("newsUpdateCompleted"));
				}

				if (data.status === "failed") {
					throw new Error(data.message);
				}
			} catch (error) {
				cleanupPolling();
				setIsUpdateAvailable(true);
				setUpdateButtonText(getLatestNewsText("DEFAULT"));
				localStorage.removeItem(STORAGE_KEY);

				// dispatch failure event
				window.dispatchEvent(new CustomEvent("newsUpdateFailed"));
			}
		}, 5000);
	}, [cleanupPolling]);

	// Load from localStorage on mount
	useEffect(() => {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored) {
			try {
				const state: StoredState = JSON.parse(stored);
				if (state.nextAvailableTime) {
					const now = Date.now();
					if (now < state.nextAvailableTime) {
						setNextAvailableTime(state.nextAvailableTime);
						setIsUpdateAvailable(false);
						const minutesLeft = Math.ceil(
							(state.nextAvailableTime - now) / 60000
						);
						setMinutesRemaining(minutesLeft);
					} else {
						// Time has passed, clear storage
						localStorage.removeItem(STORAGE_KEY);
					}
				}
				// Resume polling if it was in progress
				if (state.isPolling && state.pollingStartTime) {
					const now = Date.now();
					const elapsed = now - state.pollingStartTime;
					const POLLING_TIMEOUT = 2 * 60 * 1000;

					if (elapsed < POLLING_TIMEOUT) {
						// Resume polling
						setIsPolling(true);
						pollingStartTimeRef.current = state.pollingStartTime;
						setIsUpdateAvailable(false);
						setUpdateButtonText(getLatestNewsText("LOADING"));
						startPolling();
					} else {
						// Polling timed out while away
						localStorage.removeItem(STORAGE_KEY);
					}
				}
			} catch (error) {
				console.error("Failed to parse stored news update state:", error);
				localStorage.removeItem(STORAGE_KEY);
			}
		}
	}, [startPolling]);

	// Save to localStorage when state changes
	useEffect(() => {
		if (nextAvailableTime !== null || isPolling) {
			const state: StoredState = {
				nextAvailableTime,
				isUpdateAvailable: false,
				isPolling,
				pollingStartTime: pollingStartTimeRef.current || undefined,
			};
			localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
		} else if (!isPolling && nextAvailableTime === null) {
			localStorage.removeItem(STORAGE_KEY);
		}
	}, [nextAvailableTime, isPolling]);

	// Countdown timer - updates every minute
	useEffect(() => {
		if (nextAvailableTime === null) return;

		const updateCountdown = () => {
			const now = Date.now();
			if (now >= nextAvailableTime) {
				// Time is up
				setIsUpdateAvailable(true);
				setUpdateButtonText("Update latest news");
				setNextAvailableTime(null);
				setMinutesRemaining(null);
				localStorage.removeItem(STORAGE_KEY);
			} else {
				const minutesLeft = Math.ceil((nextAvailableTime - now) / 60000);
				setMinutesRemaining(minutesLeft);
				setUpdateButtonText(
					`Updated recently. Try in ${minutesLeft} minute${
						minutesLeft !== 1 ? "s" : ""
					}.`
				);
			}
		};

		// Update immediately
		updateCountdown();

		// Then update every minute
		const interval = setInterval(updateCountdown, 60000);

		return () => clearInterval(interval);
	}, [nextAvailableTime]);

	// Cleanup on unmount
	useEffect(() => {
		return () => {
			cleanupPolling();
		};
	}, [cleanupPolling]);

	// Trigger update function
	const triggerUpdate = useCallback(async () => {
		// Set loading state immediately
		setIsUpdateAvailable(false);
		setUpdateButtonText(getLatestNewsText("LOADING"));
		try {
			const response = await fetch(`${API_BASE_URL}/api/sentiment/update`, {
				method: "POST",
			});

			if (response.status === 429) {
				const data = await response.json();
				const minutesUntilNext = data.minutesUntilNextUpdate;

				const nextAvailable = Date.now() + minutesUntilNext * 60 * 1000;
				setNextAvailableTime(nextAvailable);

				setUpdateButtonText(getLatestNewsText("UNAVAILABLE", minutesUntilNext));
				setIsUpdateAvailable(false);
				return;
			}

			if (response.status === 202) {
				setIsPolling(true);
				pollingStartTimeRef.current = Date.now();
				startPolling();
			}
			if (!response.ok) {
				throw new Error();
			}
		} catch (error) {
			setIsUpdateAvailable(true);
			setUpdateButtonText(getLatestNewsText("DEFAULT"));
			window.dispatchEvent(new CustomEvent("newsUpdateFailed"));
		}
	}, [startPolling]);

	return (
		<NewsUpdateContext.Provider
			value={{
				isUpdateAvailable,
				updateButtonText,
				minutesRemaining,
				triggerUpdate,
				isPolling,
			}}
		>
			{children}
		</NewsUpdateContext.Provider>
	);
};

export const useNewsUpdate = () => {
	const context = useContext(NewsUpdateContext);
	if (context === undefined) {
		throw new Error("useNewsUpdate must be used within a NewsUpdateProvider");
	}
	return context;
};

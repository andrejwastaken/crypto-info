import type { TimePeriod } from "../types";

export const periodToSize: Record<TimePeriod, number | null> = {
	"7D": 7,
	"1M": 30,
	"3M": 90,
	"1Y": 365,
	Max: null, // no limit
};

export const SIGNAL_ZONES = [
	{
		limit: 15,
		label: "Strong Sell",
		color: "text-red-600",
		gaugeColor: "#DC2626",
		showTick: false,
	},
	{
		limit: 35,
		label: "Sell",
		color: "text-red-500",
		gaugeColor: "#EF4444",
		showTick: true,
	},
	{
		limit: 65,
		label: "Hold",
		color: "text-yellow-500",
		gaugeColor: "#F59E0B",
		showTick: true,
	},
	{
		limit: 85,
		label: "Buy",
		color: "text-green-500",
		gaugeColor: "#22C55E",
		showTick: false,
	},
	{
		limit: 100,
		label: "Strong Buy",
		color: "text-green-600",
		gaugeColor: "#16A34A",
		showTick: false,
	},
];

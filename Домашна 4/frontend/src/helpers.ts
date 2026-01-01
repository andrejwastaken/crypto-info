export const formatNumber = (num: number): string => {
	if (num === 0) return "0";

	const absNum = Math.abs(num);
	const sign = num < 0 ? "-" : "";

	// large numbers: truncate the zeroes
	if (absNum >= 1_000_000_000_000) {
		return sign + (absNum / 1_000_000_000_000).toFixed(3) + "T";
	}
	if (absNum >= 1_000_000_000) {
		return sign + (absNum / 1_000_000_000).toFixed(3) + "B";
	}
	if (absNum >= 1_000_000) {
		return sign + (absNum / 1_000_000).toFixed(3) + "M";
	}
	if (absNum >= 1_000) {
		return sign + (absNum / 1_000).toFixed(3) + "K";
	}

	// numbers >= 10: show with 3 decimal places and thousand separators
	if (absNum >= 10) {
		return num.toLocaleString(undefined, {
			minimumFractionDigits: 3,
			maximumFractionDigits: 3,
		});
	}

	// numbers >= 0.0001: show with up to 5 decimal places
	if (absNum >= 0.0001) {
		return num.toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 5,
		});
	}

	// small decimals: show enough precision
	const str = num.toString();
	const match = str.match(/^-?0\.0*/);
	if (match) {
		const zerosAfterDecimal = match[0].length - 2;
		return num.toFixed(zerosAfterDecimal + 2);
	}
	return num.toFixed(2);
};

export const formatPrice = (num: number): string => {
	// format price without K, M, B, T suffixes - shows full number with commas
	if (num === 0) return "0";

	const absNum = Math.abs(num);

	// numbers >= 10: show with 3 decimal places and thousand separators
	if (absNum >= 10) {
		return num.toLocaleString(undefined, {
			minimumFractionDigits: 3,
			maximumFractionDigits: 3,
		});
	}

	// numbers >= 0.0001: show with up to 5 decimal places
	if (absNum >= 0.0001) {
		return num.toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 5,
		});
	}

	// small decimals: show enough precision
	const str = num.toString();
	const match = str.match(/^-?0\.0*/);
	if (match) {
		const zerosAfterDecimal = match[0].length - 2;
		return num.toFixed(zerosAfterDecimal + 2);
	}
	return num.toFixed(2);
};

export const formatNumberChainMetrics = (num: number): string => {
	const formattedNum: string = formatNumber(num);
	if (
		formattedNum.includes(".") &&
		!formattedNum.substring(formatNumber.length - 1).match(/^[A-Za-z]+$/) &&
		formattedNum.endsWith("0")
	) {
		return formattedNum.substring(0, formattedNum.length - 1);
	}
	return formattedNum;
};

// Sentiment analysis helper

export const mapSentiment = (
	label: string
): "Positive" | "Negative" | "Neutral" => {
	const lowerLabel = label.toLowerCase();
	if (lowerLabel.includes("positive")) return "Positive";
	if (lowerLabel.includes("negative")) return "Negative";
	return "Neutral";
};

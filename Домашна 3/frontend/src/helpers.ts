export const formatNumber = (num: number): string => {
	if (num === 0) return "0";

	const absNum = Math.abs(num);
	const sign = num < 0 ? "-" : "";

	// large numbers: truncate the zeroes
	if (absNum >= 1_000_000_000_000) {
		return sign + (absNum / 1_000_000_000_000).toFixed(2) + "T";
	}
	if (absNum >= 1_000_000_000) {
		return sign + (absNum / 1_000_000_000).toFixed(2) + "B";
	}
	if (absNum >= 1_000_000) {
		return sign + (absNum / 1_000_000).toFixed(2) + "M";
	}
	if (absNum >= 1_000) {
		return sign + (absNum / 1_000).toFixed(2) + "K";
	}

	// numbers >= 1: show with 2 decimal places and thousand separators
	if (absNum >= 1) {
		return num.toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2,
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

	// numbers >= 1: show with 2 decimal places and thousand separators
	if (absNum >= 1) {
		return num.toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2,
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

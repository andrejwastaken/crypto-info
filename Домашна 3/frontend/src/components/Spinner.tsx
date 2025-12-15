const Spinner = ({
	size = "md",
	color = "amber",
}: {
	size?: "sm" | "md" | "lg";
	color?: "amber" | "slate";
}) => {
	const sizeClasses = {
		sm: "w-4 h-4 border-2",
		md: "w-8 h-8 border-3",
		lg: "w-12 h-12 border-4",
	};

	const colorClasses = {
		amber: "border-amber-500 border-t-transparent",
		slate: "border-slate-500 border-t-transparent",
	};

	return (
		<div
			className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full animate-spin`}
		/>
	);
};

export default Spinner;

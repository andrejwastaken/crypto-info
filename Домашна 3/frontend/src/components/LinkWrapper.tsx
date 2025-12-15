interface LinkWrapperProps {
	link: string;
	text: string;
	endWithBlankSpace?: boolean;
}

const LinkWrapper = ({
	link,
	text,
	endWithBlankSpace = true,
}: LinkWrapperProps) => (
	<a
		href={link}
		target="_blank"
		rel="noopener noreferrer"
		className="text-blue-800 hover:underline"
	>
		{text}
		{endWithBlankSpace ? " " : ""}
	</a>
);

export default LinkWrapper;

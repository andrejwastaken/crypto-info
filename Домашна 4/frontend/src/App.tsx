import { createBrowserRouter, Outlet, RouterProvider } from "react-router-dom";
import Footer from "./components/Footer";
import Nav from "./components/Nav";
import { CoinsProvider } from "./context/CoinsContext";
import AboutPage from "./pages/AboutPage";
import CoinPage from "./pages/CoinPage";
import HowItWorksPage from "./pages/HowItWorksPage";
import LandingPage from "./pages/LandingPage";

const Layout = () => (
	<div className="flex flex-col min-h-screen">
		<Nav />
		<main className="grow">
			<Outlet />
		</main>
		<Footer />
	</div>
);

const router = createBrowserRouter([
	{
		path: "/",
		element: <Layout />,
		children: [
			{ path: "", element: <LandingPage /> },
			{ path: "coins/:symbol", element: <CoinPage /> },
			{ path: "how-it-works", element: <HowItWorksPage /> },
			{ path: "about", element: <AboutPage /> },
		],
	},
]);

const App = () => {
	return (
		<CoinsProvider>
			<RouterProvider router={router} />
		</CoinsProvider>
	);
};

export default App;

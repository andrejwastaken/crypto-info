import { useEffect } from "react";
import { createBrowserRouter, Outlet, RouterProvider } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import Footer from "./components/Footer";
import Nav from "./components/Nav";
import { CoinsProvider } from "./context/CoinsContext";
import { NewsUpdateProvider } from "./context/NewsUpdateContext";
import AboutPage from "./pages/AboutPage";
import CoinPage from "./pages/CoinPage";
import HowItWorksPage from "./pages/HowItWorksPage";
import LandingPage from "./pages/LandingPage";

const Layout = () => (
	<div className="flex flex-col min-h-screen">
		<Nav />
		<main className="grow">
			<Outlet />
			<ToastContainer />
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
	useEffect(() => {
		const handleUpdateComplete = () => {
			setTimeout(() => {
				toast.success(
					<div className="text-slate-700">
						<div className="font-bold mb-1">News Update Finished</div>
						<div className="text-sm ">The latest news have been updated.</div>
					</div>,
					{
						position: "top-right",
						autoClose: 2000,
						hideProgressBar: false,
						closeOnClick: true,
						pauseOnHover: true,
						draggable: true,
						theme: "light",
						className: "border shadow-xl backdrop-blur-xl",
						progressClassName: "bg-green-500",
					}
				);
			}, 100);
		};

		const handleUpdateFailed = () => {
			setTimeout(() => {
				toast.error(
					<div className="text-slate-700">
						<div className="font-bold mb-1">News Update Failed</div>
						<div className="text-sm ">
							Please try again in a couple of minutes.
						</div>
					</div>,
					{
						position: "top-right",
						autoClose: 2000,
						hideProgressBar: false,
						closeOnClick: true,
						pauseOnHover: true,
						draggable: true,
						theme: "light",
						className: "border shadow-xl backdrop-blur-xl",
						progressClassName: "bg-red-500",
					}
				);
			}, 100);
		};

		window.addEventListener("newsUpdateCompleted", handleUpdateComplete);
		window.addEventListener("newsUpdateFailed", handleUpdateFailed);
		return () => {
			window.removeEventListener("newsUpdateCompleted", handleUpdateComplete);
			window.removeEventListener("newsUpdateFailed", handleUpdateFailed);
		};
	}, []);
	return (
		<CoinsProvider>
			<NewsUpdateProvider>
				<RouterProvider router={router} />
			</NewsUpdateProvider>
		</CoinsProvider>
	);
};

export default App;

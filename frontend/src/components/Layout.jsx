import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
    return (
        <main className="App">
            <Navbar></Navbar>
            <Outlet />
        </main>
    )
}
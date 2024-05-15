import React, { useState } from 'react'
import Navbar from './components/Navbar'
import Products from './pages/Products'

export default function App() {
  const [products, setProducts] = useState([])

  const fetchProducts = async () => {
    const response = await fetch()
  }

  return (
    <div>
      <Navbar />
      <Products />
    </div>
  );
}


import React, { useState } from 'react'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import Categories from './pages/Categories'
import Brands from './pages/Brands';
import Products from './pages/Products';
import Users from './pages/Users';
import RequireAuth from './components/RequireAuth';
import Order from './pages/Order';
import Unauthorized from './pages/Unauthorized';

import Cookies from "universal-cookie";

export const cookies = new Cookies()

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}> 
        <Route element={<RequireAuth allowedRoles={["manager","admin"]} />}>
          <Route path="admin/categories" element={<Categories />}/> 
          <Route path="admin/brands" element={<Brands />}/>
          <Route path="admin/create-product" element={<Products />}/> 
          <Route path="admin/product" element={<Products />}/>
        </Route>

        <Route element={<RequireAuth allowedRoles={["admin"]} />}>
            <Route path="admin/users" element={<Users />}/>
        </Route>

        <Route path="product" element={<Products />}/>
        <Route path="login" element={<Login />}/>
        <Route path="order" element={<Order />}/>
        <Route path="unauthorized" element={<Unauthorized />}/>
      </Route>
    </Routes>
  )
}


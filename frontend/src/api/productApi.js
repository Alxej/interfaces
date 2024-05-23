

import React from 'react'
import axios from './axios'
import { cookies } from '../App'

const headers = {
    'Content-Type' : 'application/json',
    'Authorization': `Bearer ${cookies.get("token")}`
}

export default function getProducts(page, per_page) {
    const response = axios.get(`api/ProductApi/products?page=${page}?per_page=${per_page}`,
        JSON.stringify({username, password}),
        {
            headers: headers
        }
    )
  return (
    response
  )
}



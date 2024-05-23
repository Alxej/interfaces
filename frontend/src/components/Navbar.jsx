import React from 'react'
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { Link } from 'react-router-dom';


export default function Navbar() {
  return (
    <div>
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Store
                    </Typography>
                    <Button component={Link} to="/admin/product" color="inherit">Products</Button>
                    <Button component={Link} to="/admin/categories" color="inherit">Categories</Button>
                    <Button component={Link} to="/admin/brands" color="inherit">Brands</Button>
                    <Button component={Link} to="/admin/login" color="inherit">Login</Button>
                </Toolbar>
            </AppBar>
        </Box>
    </div>
  );
}

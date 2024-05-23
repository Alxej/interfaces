import React, { useState } from 'react'
import useAuth from '../hooks/useAuth';
import { Grid, Paper, TextField, Avatar, Button } from '@mui/material'
import {jwtDecode} from "jwt-decode";
import axios  from '../api/axios';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { cookies } from '../App';

const LOGIN_URL = '/api/UserApi/login'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('')

  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || "/"

  const {setAuth} = useAuth();
  const token = sessionStorage.getItem("token");
  
  const logout = () => {
    setUsername(null);
    cookies.remove("token")
    cookies.remove("role")
    cookies.remove("user")
  }

  const login = (token, role) => {
    const decoded = jwtDecode(token);
    cookies.set("token", token, {
        expires: new Date(decoded.exp * 100000),
        path: "/"
    });
    cookies.set("role", role, {
        expires: new Date(decoded.exp * 100000)
    });
    cookies.set("user", decoded, {
        expires: new Date(decoded.exp * 100000)
    });
    console.log(decoded)
  };

  const handleClick = async (e) => {
    e.preventDefault()
    try {
        const response = await axios.post(LOGIN_URL,
            JSON.stringify({username, password}),
            {
                headers: {'Content-Type' : 'application/json'},
            }
        )
        console.log(JSON.stringify(response.data))
        const accessToken = response.data.access_token
        const role = response.data.role
        setAuth({username, password, role, accessToken})
        login(accessToken, role)
        setUsername('')
        setPassword('')
        navigate(from, { replace: true })
    } catch (err) {
        console.error("Getting token error", err)
    }
    
    // const options = {
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json"
    //     },
    //     body: JSON.stringify({
    //         "username": username,
    //         "password": password
    //     })
    // }
    // fetch('http://127.0.0.1:5000/api/UserApi/login', options)
    //     .then(resp => {
    //         if(resp.status === 201) return resp.json();
    //         else alert("Server error");
    //     })
    //     .then(data => {
    //         const token = data.access_token
    //         const role = data.role
    //         setAuth({username, password, role, token})
    //         login(data.access_token)
    //         setSuccess(true)
    //     })
    //     .catch(error => {
    //         console.error("Getting token error", error)
    //     })

  }


  const paperStyle = {
    padding: 20,
    height: '50vh',
    width: 280,
    margin: "20px auto"
  }

  const avatarStyle = {
    backgroundColor: '#1bbd7e'
  }

  const gridStyle = {
    margin: "10px auto",
  }

  return (
    <Grid>
        <Paper elevation={10} style={paperStyle}>
            <Grid align='center'>
                <Avatar style={avatarStyle}><LockOpenIcon/></Avatar>
                <h2>Sign In</h2>
            </Grid>
            <Grid>
                <Grid item>
                    <TextField variant='outlined' label="Username" placeholder='Enter username' fullWidth required value={username} onChange={(e) => setUsername(e.target.value)}/>
                </Grid>
                <Grid item style={gridStyle}>
                    <TextField variant='outlined' label="Password" placeholder='Enter password' type='password' fullWidth required value={password} onChange={(e) => setPassword(e.target.value)}/>
                </Grid>
                <Grid item style={gridStyle}>
                    <Button type='submit' color="primary" variant='contained' fullWidth onClick={handleClick}>Sign In</Button>
                </Grid>
            </Grid>    
        </Paper>
    </Grid>
  )
}

import { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    const api = axios.create({
        baseURL: '/api',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }

    useEffect(() => {
        const loadUser = async () => {
            if (token) {
                try {
                    const res = await api.get('/auth/me');
                    setUser(res.data);
                } catch (err) {
                    console.error("Auth check failed", err);
                    logout();
                }
            }
            setLoading(false);
        };
        loadUser();
    }, [token]);

    const login = async (email, password) => {
        const res = await api.post('/auth/login', { email, password });
        const { access_token, user } = res.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(user);
        return user;
    };

    const register = async (username, email, password) => {
        const res = await api.post('/auth/register', { username, email, password });
        const { access_token, user } = res.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(user);
        return user;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        delete api.defaults.headers.common['Authorization'];
    };

    const updateProfile = async (data) => {
        const res = await api.put('/auth/update', data);
        setUser(res.data.user);
        return res.data;
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, updateProfile, loading, api }}>
            {children}
        </AuthContext.Provider>
    );
};

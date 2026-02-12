import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Background3D from '../components/Background3D';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="row justify-content-center align-items-center vh-100"
        >
            <div className="col-12 col-md-6 col-lg-4">
                <div className="card shadow-lg border-0 rounded-4">
                    <div className="card-body p-5">
                        <h2 className="text-center mb-4 fw-bold text-primary">Login</h2>
                        {error && <div className="alert alert-danger glass-card border-danger">{error}</div>}

                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label className="form-label">Email Address</label>
                                <input
                                    type="email"
                                    className="form-control form-control-lg"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    placeholder="name@example.com"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="form-label">Password</label>
                                <input
                                    type="password"
                                    className="form-control form-control-lg"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    placeholder="Enter your password"
                                />
                            </div>
                            <button type="submit" className="btn btn-primary w-100 btn-lg mb-3 shadow">Sign In</button>
                        </form>
                        <p className="text-center text-muted mt-4">
                            Don't have an account? <Link to="/register" className="text-decoration-none fw-bold">Register</Link>
                        </p>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Login;

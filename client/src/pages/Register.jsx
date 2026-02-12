import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Background3D from '../components/Background3D';

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await register(username, email, password);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.msg || 'Registration failed');
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="row justify-content-center align-items-center vh-100"
        >
            <div className="col-12 col-md-6 col-lg-4">
                <div className="card glass-card shadow-lg border-0 rounded-4">
                    <div className="card-body p-5">
                        <h2 className="text-center mb-4 fw-bold text-white">Register</h2>
                        {error && <div className="alert alert-danger glass-card border-danger">{error}</div>}
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label className="form-label text-white">Username</label>
                                <input
                                    type="text"
                                    className="form-control glass-input"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="mb-3">
                                <label className="form-label text-white">Email</label>
                                <input
                                    type="email"
                                    className="form-control glass-input"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="mb-3">
                                <label className="form-label text-white">Password</label>
                                <input
                                    type="password"
                                    className="form-control glass-input"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className="btn btn-primary w-100 py-2 fw-bold shadow-lg">Register</button>
                        </form>
                        <div className="mt-3 text-center text-muted">
                            <small>Already have an account? <Link to="/login" className="text-primary fw-bold">Login here</Link></small>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Register;

import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const Dashboard = () => {
    const { api, user } = useAuth();
    const [estimations, setEstimations] = useState([]);
    const [stats, setStats] = useState({ count: 0, total_value: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/data/dashboard');
                setEstimations(res.data.estimations);
                setStats({ count: res.data.count, total_value: res.data.total_value });
            } catch (err) {
                console.error(err);
            }
            setLoading(false);
        };
        fetchData();
    }, [api]);

    if (loading) return <div className="text-center mt-5"><div className="spinner-border"></div></div>;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="container"
        >
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 className="fw-bold">Welcome, {user.username}!</h2>
                    <p className="text-muted">Here is your project overview</p>
                </div>
                <Link to="/estimate" className="btn btn-primary btn-lg shadow">+ New Estimate</Link>
            </div>

            <div className="row mb-4">
                <div className="col-md-6">
                    <div className="card glass-card border-0 shadow-lg p-3 rounded-4 h-100">
                        <div className="card-body">
                            <h5 className="text-secondary">Total Projects</h5>
                            <h2 className="fw-bold display-4 text-white">{stats.count}</h2>
                        </div>
                    </div>
                </div>
                <div className="col-md-6">
                    <div className="card glass-card border-0 shadow-lg p-3 rounded-4 h-100">
                        <div className="card-body">
                            <h5 className="text-secondary">Total Estimated Value</h5>
                            <h2 className="fw-bold display-4 text-primary">Rs. {stats.total_value.toLocaleString()}</h2>
                        </div>
                    </div>
                </div>
            </div>

            <h4 className="fw-bold mb-3 text-white">Recent Estimations</h4>
            {estimations.length === 0 ? (
                <div className="alert alert-info glass-card">No estimations found. Start a new one!</div>
            ) : (
                <div className="table-responsive glass-card rounded-4 p-2 shadow-lg">
                    <table className="table table-dark table-hover mb-0">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>City</th>
                                <th>Total Cost (INR)</th>
                                <th>2026 Prediction</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {estimations.map((est) => (
                                <tr key={est.id}>
                                    <td>{est.date}</td>
                                    <td>{est.city}</td>
                                    <td className="fw-bold">Rs. {est.total_cost.toLocaleString()}</td>
                                    <td className="text-muted">Rs. {est.predicted_2026.toLocaleString()}</td>
                                    <td>
                                        <Link to={`/result/${est.id}`} className="btn btn-sm btn-outline-primary">View</Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </motion.div>
    );
};

export default Dashboard;

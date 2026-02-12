import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const Result = () => {
    const { id } = useParams();
    const { api } = useAuth();
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchResult = async () => {
            try {
                const res = await api.get(`/data/result/${id}`);
                setData(res.data);
            } catch (err) {
                console.error(err);
                setError(err.response?.data?.msg || 'Failed to load estimation');
            }
            setLoading(false);
        };
        fetchResult();
    }, [id, api]);

    if (loading) return <div className="text-center mt-5"><div className="spinner-border"></div></div>;
    if (error) return <div className="alert alert-danger text-center mt-5">{error}</div>;
    if (!data) return <div className="alert alert-danger text-center mt-5">Estimation data unavailable</div>;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="container pb-5"
        >
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="fw-bold">Estimation Result <span className="text-muted fs-5">| {data.date}</span></h2>
                <Link to="/dashboard" className="btn btn-outline-secondary">Back to Dashboard</Link>
            </div>

            <div className="row g-4">
                {/* Highlights */}
                <div className="col-md-6">
                    <div className="card glass-card border-0 shadow-lg p-4 rounded-4 h-100">
                        <h4 className="text-secondary">Estimated Total Cost</h4>
                        <h1 className="fw-bold display-4 text-primary">Rs. {data.total_cost.toLocaleString()}</h1>
                        <p className="mb-0 opacity-75">Current Market Rates</p>
                    </div>
                </div>
                <div className="col-md-6">
                    <div className="card glass-card border-0 shadow-lg p-4 rounded-4 h-100">
                        <h4 className="text-secondary">2026 Forecast Price</h4>
                        <h1 className="fw-bold display-4 text-info">Rs. {Math.round(data.predicted_2026).toLocaleString()}</h1>
                        <p className="mb-0 opacity-75">Projected Inflation Impact</p>
                    </div>
                </div>

                {/* Quantities */}
                <div className="col-md-12">
                    <div className="card glass-card border-0 shadow-lg rounded-4">
                        <div className="card-header bg-transparent border-bottom border-secondary py-3">
                            <h5 className="fw-bold mb-0 text-white">Material Quantities</h5>
                        </div>
                        <div className="card-body">
                            <div className="table-responsive">
                                <table className="table table-dark table-hover mb-0">
                                    <thead>
                                        <tr>
                                            <th>Material</th>
                                            <th>Quantity</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {Object.entries(data.quantities).map(([key, val]) => (
                                            <tr key={key}>
                                                <td className="text-capitalize">{key.replace('_', ' ')}</td>
                                                <td className="fw-bold">{val.toLocaleString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Cost Breakdown */}
                <div className="col-md-12">
                    <div className="card glass-card border-0 shadow-lg rounded-4">
                        <div className="card-header bg-transparent border-bottom border-secondary py-3">
                            <h5 className="fw-bold mb-0 text-white">Cost Breakdown</h5>
                        </div>
                        <div className="card-body">
                            <div className="table-responsive">
                                <table className="table table-dark table-hover mb-0">
                                    <thead>
                                        <tr>
                                            <th>Item</th>
                                            <th className="text-end">Cost (INR)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {Object.entries(data.breakdown).map(([key, val]) => (
                                            <tr key={key}>
                                                <td className="text-capitalize">{key}</td>
                                                <td className="text-end fw-bold">Rs. {val.toLocaleString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="alert alert-success glass-card border-success mt-4 d-flex align-items-center text-white">
                <i className="bi bi-check-circle-fill me-2 fs-4 text-success"></i>
                <div>
                    <strong>Report Sent!</strong> A detailed PDF report has been emailed to you.
                </div>
            </div>
        </motion.div>
    );
};

export default Result;

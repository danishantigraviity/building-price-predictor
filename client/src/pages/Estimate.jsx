import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Estimate = () => {
    const { api } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        city: 'Chennai',
        quality: 'standard',
        floors: 2,
        area_sqft: '',
        rooms: '',
        wall_length: '',
        carpet_ratio: 0.72,
        is_commercial: false
    });
    const [blueprint, setBlueprint] = useState(null);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleFileChange = (e) => {
        setBlueprint(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const data = new FormData();
        Object.keys(formData).forEach(key => {
            if (formData[key] !== '') data.append(key, formData[key]);
        });
        if (blueprint) data.append('blueprint', blueprint);

        try {
            const res = await api.post('/data/estimate', data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            navigate(`/result/${res.data.id}`);
        } catch (err) {
            setError(err.response?.data?.msg || 'Estimation failed. Please check your inputs and try again.');
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="row justify-content-center mb-5"
        >
            <div className="col-12 col-lg-8">
                <div className="card glass-card shadow-lg border-0 rounded-4">
                    <div className="card-header border-0 pt-4 px-5 bg-transparent">
                        <h3 className="fw-bold text-white">New Construction Estimate</h3>
                        <p className="text-muted">Fill in the details below to get a precise cost estimation.</p>
                    </div>
                    <div className="card-body px-5 pb-5">
                        {error && <div className="alert alert-danger glass-card border-danger">{error}</div>}

                        <form onSubmit={handleSubmit}>
                            <div className="row g-3">
                                <div className="col-md-6">
                                    <label className="form-label text-white">City</label>
                                    <select name="city" className="form-select glass-input" value={formData.city} onChange={handleChange}>
                                        <option value="Chennai">Chennai</option>
                                        <option value="Bengaluru">Bengaluru</option>
                                        <option value="Coimbatore">Coimbatore</option>
                                        <option value="Mumbai">Mumbai</option>
                                        <option value="Delhi">Delhi</option>
                                        <option value="Hyderabad">Hyderabad</option>
                                        <option value="Ahmedabad">Ahmedabad</option>
                                    </select>
                                </div>
                                <div className="col-md-6">
                                    <label className="form-label text-white">Quality Grade</label>
                                    <select name="quality" className="form-select glass-input" value={formData.quality} onChange={handleChange}>
                                        <option value="basic">Basic</option>
                                        <option value="standard">Standard</option>
                                        <option value="premium">Premium</option>
                                    </select>
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label text-white">Floors</label>
                                    <input type="number" name="floors" className="form-control glass-input" value={formData.floors} onChange={handleChange} required />
                                </div>
                                <div className="col-md-4">
                                    <label className="form-label text-white">Carpet Ratio</label>
                                    <input type="number" step="0.01" name="carpet_ratio" className="form-control glass-input" value={formData.carpet_ratio} onChange={handleChange} />
                                </div>
                                <div className="col-md-4 d-flex align-items-center mt-4 pt-2">
                                    <div className="form-check">
                                        <input className="form-check-input" type="checkbox" name="is_commercial" checked={formData.is_commercial} onChange={handleChange} />
                                        <label className="form-check-label text-white">Is Commercial?</label>
                                    </div>
                                </div>

                                <h5 className="mt-4 border-bottom border-secondary pb-2 text-white">Manual Overrides</h5>

                                <div className="col-md-4">
                                    <label className="form-label text-white">Area (sqft)</label>
                                    <input type="number" name="area_sqft" className="form-control glass-input" value={formData.area_sqft} onChange={handleChange} placeholder="Optional" />
                                </div>
                                <div className="col-md-4">
                                    <label className="form-label text-white">Rooms</label>
                                    <input type="number" name="rooms" className="form-control glass-input" value={formData.rooms} onChange={handleChange} placeholder="Optional" />
                                </div>
                                <div className="col-md-4">
                                    <label className="form-label text-white">Wall Length (ft)</label>
                                    <input type="number" name="wall_length" className="form-control glass-input" value={formData.wall_length} onChange={handleChange} placeholder="Optional" />
                                </div>

                                <div className="col-12 mt-3">
                                    <label className="form-label fw-bold text-white">Upload Blueprint Image (Auto-Extraction)</label>
                                    <input type="file" className="form-control glass-input" accept="image/*" onChange={handleFileChange} />
                                    <small className="text-muted">If uploaded, we will try to estimate area and rooms automatically.</small>
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary w-100 py-3 mt-4 fw-bold shadow-lg" disabled={loading}>
                                {loading ? 'Calculating...' : 'Generate Estimate'}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Estimate;

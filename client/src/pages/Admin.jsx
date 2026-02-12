import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Admin = () => {
    const { api } = useAuth();
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const statsRes = await api.get('/admin/stats');
                const usersRes = await api.get('/admin/users');
                setStats(statsRes.data);
                setUsers(usersRes.data);
            } catch (err) {
                console.error(err);
            }
            setLoading(false);
        };
        fetchData();
    }, [api]);

    if (loading) return <div className="text-center mt-5"><div className="spinner-border"></div></div>;
    if (!stats) return <div className="alert alert-danger">Error loading admin data</div>;

    return (
        <div className="container">
            <h2 className="fw-bold mb-4 text-primary">Admin Dashboard</h2>

            <div className="row g-4 mb-4">
                <div className="col-md-4">
                    <div className="card border-0 shadow-sm bg-info text-white rounded-3">
                        <div className="card-body">
                            <h5>Total Users</h5>
                            <h3>{stats.total_users}</h3>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card border-0 shadow-sm bg-warning text-dark rounded-3">
                        <div className="card-body">
                            <h5>Total Estimations</h5>
                            <h3>{stats.total_estimations}</h3>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card border-0 shadow-sm bg-success text-white rounded-3">
                        <div className="card-body">
                            <h5>Total Predictions</h5>
                            <h3>{stats.total_predictions}</h3>
                        </div>
                    </div>
                </div>
            </div>

            <div className="card border-0 shadow rounded-3">
                <div className="card-header bg-white py-3">
                    <h5 className="mb-0 fw-bold">User Management</h5>
                </div>
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table table-hover mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(u => (
                                    <tr key={u.id}>
                                        <td>{u.id}</td>
                                        <td>{u.username}</td>
                                        <td>{u.email}</td>
                                        <td>
                                            {u.is_admin ?
                                                <span className="badge bg-danger">Admin</span> :
                                                <span className="badge bg-secondary">User</span>
                                            }
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Admin;

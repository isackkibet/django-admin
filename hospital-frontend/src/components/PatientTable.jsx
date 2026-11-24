const patients = [
  { id: 'PAT-001', name: 'Alex Morgan', email: 'alex@gmail.com', phone: '+254 700 123 456', active: true },
  { id: 'PAT-002', name: 'Felix Otieno', email: 'felix@gmail.com', phone: '+254 712 345 678', active: true },
  { id: 'PAT-003', name: 'Amina Hassan', email: 'amina@gmail.com', phone: '+254 733 987 654', active: false },
]

function PatientTable() {
  return (
    <div className="card table-card">
      <div className="card-body">
        <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
          <div>
            <h5 className="fw-bold">Patient Records</h5>
            <small className="text-muted">Manage patient information</small>
          </div>
          <button type="button" className="btn btn-primary">
            <i className="bi bi-plus-circle me-1"></i>
            Add Patient
          </button>
        </div>

        <div className="row mb-3">
          <div className="col-md-4">
            <input type="text" className="form-control" placeholder="Search patient..." />
          </div>
        </div>

        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((patient) => (
                <tr key={patient.id}>
                  <td><span className="fw-semibold">{patient.id}</span></td>
                  <td>{patient.name}</td>
                  <td>
                    <a href={`mailto:${patient.email}`} className="text-decoration-none">
                      {patient.email}
                    </a>
                  </td>
                  <td>{patient.phone}</td>
                  <td>
                    <span className={`badge rounded-pill bg-${patient.active ? 'success' : 'secondary'}-subtle text-${patient.active ? 'success' : 'secondary'}`}>
                      {patient.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div className="d-flex gap-2">
                      <button type="button" className="btn btn-sm btn-outline-primary" title="View patient">
                        <i className="bi bi-eye"></i>
                      </button>
                      <button type="button" className="btn btn-sm btn-outline-warning" title="Edit patient">
                        <i className="bi bi-pencil-square"></i>
                      </button>
                      <button type="button" className="btn btn-sm btn-outline-danger" title="Delete patient">
                        <i className="bi bi-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default PatientTable

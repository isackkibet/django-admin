import { useState } from 'react'

const initialPatients = [
  { id: 'PAT-001', name: 'Alex Morgan', email: 'alex@gmail.com', phone: '+254 700 123 456', active: true },
  { id: 'PAT-002', name: 'Felix Otieno', email: 'felix@gmail.com', phone: '+254 712 345 678', active: true },
  { id: 'PAT-003', name: 'Amina Hassan', email: 'amina@gmail.com', phone: '+254 733 987 654', active: false },
]

const emptyForm = { name: '', email: '', phone: '', active: true }

function PatientTable() {
  const [patients, setPatients] = useState(initialPatients)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)

  const handleChange = (event) => {
    const { name, value, checked, type } = event.target
    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleAddPatient = (event) => {
    event.preventDefault()

    const patient = {
      id: `PAT-${String(patients.length + 1).padStart(3, '0')}`,
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      active: form.active,
    }

    setPatients((current) => [...current, patient])
    setForm(emptyForm)
    setShowForm(false)
  }

  const closeForm = () => {
    setForm(emptyForm)
    setShowForm(false)
  }

  return (
    <div className="card table-card">
      <div className="card-body">
        <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
          <div>
            <h5 className="fw-bold">Patient Records</h5>
            <small className="text-muted">Manage patient information</small>
          </div>
          <button type="button" className="btn btn-primary" onClick={() => setShowForm(true)}>
            <i className="bi bi-plus-circle me-1"></i>
            Add Patient
          </button>
        </div>

        {showForm && (
          <form className="row g-3 mb-4" onSubmit={handleAddPatient}>
            <div className="col-md-3">
              <input
                type="text"
                name="name"
                className="form-control"
                placeholder="Full name"
                aria-label="Full name"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="col-md-3">
              <input
                type="email"
                name="email"
                className="form-control"
                placeholder="Email address"
                aria-label="Email address"
                value={form.email}
                onChange={handleChange}
              />
            </div>
            <div className="col-md-3">
              <input
                type="text"
                name="phone"
                className="form-control"
                placeholder="Phone number"
                aria-label="Phone number"
                value={form.phone}
                onChange={handleChange}
              />
            </div>
            <div className="col-md-3 d-flex align-items-center">
              <div className="form-check">
                <input
                  type="checkbox"
                  name="active"
                  id="patientActive"
                  className="form-check-input"
                  checked={form.active}
                  onChange={handleChange}
                />
                <label className="form-check-label" htmlFor="patientActive">Active</label>
              </div>
            </div>
            <div className="col-12 d-flex gap-2">
              <button type="submit" className="btn btn-success btn-sm">
                <i className="bi bi-check-circle me-1"></i>Save Patient
              </button>
              <button type="button" className="btn btn-secondary btn-sm" onClick={closeForm}>
                Cancel
              </button>
            </div>
          </form>
        )}

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

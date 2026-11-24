function PatientProfile() {
  return (
    <div className="card profile-card mb-4">
      <div className="card-body">
        <div className="d-flex justify-content-between mb-4">
          <h5 className="fw-bold">My Personal Information</h5>
          <button className="btn btn-outline-primary btn-sm">
            <i className="bi bi-pencil"></i> Edit Profile
          </button>
        </div>

        <div className="row">
          <div className="col-md-3 mb-3">
            <small className="text-muted">Patient ID</small>
            <h6>PAT-001</h6>
          </div>
          <div className="col-md-3 mb-3">
            <small className="text-muted">Full Name</small>
            <h6>Alex Morgan</h6>
          </div>
          <div className="col-md-3 mb-3">
            <small className="text-muted">Email Address</small>
            <h6>alex@gmail.com</h6>
          </div>
          <div className="col-md-3 mb-3">
            <small className="text-muted">Phone Number</small>
            <h6>+254 700 123 456</h6>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PatientProfile

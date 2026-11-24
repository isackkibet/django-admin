function Topbar() {
  return (
    <div className="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 className="fw-bold">Dashboard</h3>
        <p className="text-muted">Welcome back, Alex Morgan!</p>
      </div>

      <div className="d-flex align-items-center gap-3">
        <button className="btn btn-light">
          <i className="bi bi-bell"></i>
        </button>

        <div className="text-end">
          <strong>Alex Morgan</strong>
          <small className="d-block text-muted">Patient</small>
        </div>

        <div className="profile-image">
          <i className="bi bi-person"></i>
        </div>
      </div>
    </div>
  )
}

export default Topbar

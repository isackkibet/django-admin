function StatCard({ title, count, icon, color }) {
  return (
    <div className="col-lg-3 col-md-6">
      <div className="card dashboard-card p-3">
        <div className="d-flex justify-content-between">
          <div>
            <small className="text-muted">{title}</small>
            <h3 className="fw-bold mt-2">{count}</h3>
          </div>
          <div className={`card-icon bg-${color}-subtle text-${color}`}>
            <i className={`bi ${icon}`}></i>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatCard

const links = [
  { label: 'Dashboard', icon: 'bi-grid', active: true },
  { label: 'My Profile', icon: 'bi-person' },
  { label: 'Appointments', icon: 'bi-calendar-check' },
  { label: 'Medical Records', icon: 'bi-file-medical' },
  { label: 'Prescriptions', icon: 'bi-capsule' },
  { label: 'Billing', icon: 'bi-credit-card' },
  { label: 'Settings', icon: 'bi-gear' },
  { label: 'Logout', icon: 'bi-box-arrow-right' },
]

function Sidebar() {
  return (
    <div className="col-md-2 sidebar">
      <h4>
        <i className="bi bi-heart-pulse-fill text-info"></i>
        MediCare
      </h4>

      {links.map((link) => (
        <a href="#" className={link.active ? 'active' : ''} key={link.label}>
          <i className={`bi ${link.icon} me-2`}></i> {link.label}
        </a>
      ))}
    </div>
  )
}

export default Sidebar

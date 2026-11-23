import './App.css'
import Header from './componenents/Header.jsx'
import Sidebar from './componenents/Sidebar.jsx'
import PatientCard from './componenents/Patientcard.jsx'

function App() {
  return (
    <div className="dashboard">
      <Header />
      <Sidebar />
      <main className="dashboard-content">
        <section className="patients-section">
          <PatientCard name="Felix" age={23} gender="Male" />
          <PatientCard name="Felix" age={23} gender="Male" />
          <PatientCard name="Felix" age={23} gender="Male" />
        </section>
      </main>
    </div>
  )
}

export default App

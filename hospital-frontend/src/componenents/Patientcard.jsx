function PatientCard({ name, age, gender }) {
  return (
    <article className="patient-card">
      <h3>{name}</h3>
      <p><strong>Age:</strong> {age}</p>
      <p><strong>Gender:</strong> {gender}</p>
    </article>
  );
}

export default PatientCard;
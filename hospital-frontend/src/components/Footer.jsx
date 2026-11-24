const year = new Date().getFullYear()

function Footer() {
  return (
    <footer className="text-center py-3 mt-4 border-top">
      <p className="mb-0 text-muted">&copy; {year} Mathare Hospital. All rights reserved.</p>
    </footer>
  )
}

export default Footer

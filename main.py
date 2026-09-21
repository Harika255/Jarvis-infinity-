import sys
from PySide6.QtWidgets import QApplication
from ui.dashboard import JarvisDashboard

app = QApplication(sys.argv)

window = JarvisDashboard()
window.show()

sys.exit(app.exec())
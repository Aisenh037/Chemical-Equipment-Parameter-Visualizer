import sys
import requests
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, 
    QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

API_BASE = "http://localhost:8000/api/equipment"
AUTH = ("admin", "password123")

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EquiViz Desktop - Parameter Visualizer")
        self.resize(1000, 700)
        
        # Main Widget and Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Header
        header = QLabel("EquiViz Desktop Pro")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #6366f1;")
        self.layout.addWidget(header)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Upload & Analyze CSV")
        self.upload_btn.clicked.connect(self.upload_csv)
        self.upload_btn.setStyleSheet("padding: 10px; background-color: #6366f1; color: white; font-weight: bold;")
        toolbar_layout.addWidget(self.upload_btn)
        
        self.refresh_btn = QPushButton("Refresh History")
        self.refresh_btn.clicked.connect(self.fetch_history)
        toolbar_layout.addWidget(self.refresh_btn)
        
        self.layout.addLayout(toolbar_layout)
        
        # Stats Labels
        self.stats_label = QLabel("Summary: N/A")
        self.layout.addWidget(self.stats_label)
        
        # Charts Canvas
        self.canvas = MplCanvas(self, width=10, height=4, dpi=100)
        self.layout.addWidget(self.canvas)
        
        # Table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        
        # Initial Load
        self.fetch_history()

    def fetch_history(self):
        try:
            res = requests.get(f"{API_BASE}/history/", auth=AUTH)
            if res.status_code == 200:
                history = res.json()
                if history:
                    # Just show a message or update a list if needed, 
                    # for now we focus on the latest upload
                    pass
        except Exception as e:
            print(f"Error fetching history: {e}")

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                res = requests.post(f"{API_BASE}/upload/", files=files, auth=AUTH)
            
            if res.status_code == 201:
                data = res.json()
                self.update_ui(data)
                QMessageBox.information(self, "Success", "File uploaded and analyzed.")
            else:
                QMessageBox.warning(self, "Error", res.json().get('error', 'Upload failed'))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_ui(self, response_data):
        summary = response_data['summary']
        equip_data = response_data['data']
        
        # Update Stats Label
        stats_text = (f"Total: {summary['total_count']} | "
                      f"Avg Flow: {summary['averages']['flowrate']} | "
                      f"Avg Press: {summary['averages']['pressure']} | "
                      f"Avg Temp: {summary['averages']['temperature']}")
        self.stats_label.setText(stats_text)
        
        # Update Table
        if equip_data:
            self.table.setRowCount(len(equip_data))
            headers = list(equip_data[0].keys())
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            
            for i, row in enumerate(equip_data):
                for j, key in enumerate(headers):
                    self.table.setItem(i, j, QTableWidgetItem(str(row[key])))
        
        # Update Charts
        self.canvas.ax1.clear()
        self.canvas.ax2.clear()
        
        # Bar Chart for Averages
        params = ['Flowrate', 'Pressure', 'Temperature']
        vals = [summary['averages']['flowrate'], summary['averages']['pressure'], summary['averages']['temperature']]
        self.canvas.ax1.bar(params, vals, color='#6366f1')
        self.canvas.ax1.set_title("Average Parameters")
        
        # Pie Chart for Types
        types = list(summary['type_distribution'].keys())
        counts = list(summary['type_distribution'].values())
        self.canvas.ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=140)
        self.canvas.ax2.set_title("Equipment Distribution")
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

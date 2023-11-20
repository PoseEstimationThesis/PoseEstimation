from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsView, QFileDialog
from PySide6 import QtCharts
from PySide6.QtCore import Qt, QFile, QTextStream, QDateTime, QTimer
from PySide6.QtGui import QPainter


class GraphWidget(QWidget):
    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.layout = QVBoxLayout(self)

        self.chart_view = QtCharts.QChartView(self)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.layout.addWidget(self.chart_view)

        self.load_button = QPushButton(f"Load Data for {self.camera_id} ", self)
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)

        self.series = QtCharts.QLineSeries()
        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.axisX().setRange(0, 20000)
        self.chart.axisY().setRange(0, 360)
        self.chart.setTitle(f"CSV Data Chart for Device: {self.camera_id}")
        self.chart_view.setChart(self.chart)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)

    def load_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Load Data File", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        data_file = QFile(file_name)
        if not data_file.open(QFile.ReadOnly | QFile.Text):
            print("Failed to open file:", file_name)
            return

        self.series.clear()

        stream = QTextStream(data_file)
        header_line = stream.readLine()

        timestamps = []
        while not stream.atEnd():
            line = stream.readLine()
            values = line.split(',')
            if len(values) >= 4:
                timestamp_str = values[3]
                timestamps.append(QDateTime.fromString(timestamp_str, "yyyy-MM-dd hh:mm:ss"))

        if timestamps:
            min_timestamp = min(timestamps)

            stream.seek(0)
            header_line = stream.readLine()

            while not stream.atEnd():
                line = stream.readLine()
                values = line.split(',')
                if len(values) >= 4:
                    device_number = int(values[0])
                    timestamp_str = values[3]
                    if self.camera_id == device_number:
                        try:
                            angle = float(values[2]) if values[2] else None
                            if angle is not None:
                                timestamp = QDateTime.fromString(timestamp_str, "yyyy-MM-dd hh:mm:ss")
                                normalized_timestamp = timestamp.toMSecsSinceEpoch() - min_timestamp.toMSecsSinceEpoch()
                                self.series.append(normalized_timestamp, angle)
                        except ValueError as e:
                            print(f"Error processing line {line}: {e}")

        data_file.close()

    def update_graph(self):
        self.chart_view.repaint()

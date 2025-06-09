from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QApplication, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import QMetaObject, QCoreApplication, QRect
from PyQt5.QtGui import QFont

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("Binance Balance Checker (PyQt)")
        MainWindow.resize(450, 250) # Adjusted size for better initial view

        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)

        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # API Key Layout
        self.apiKeyLayout = QHBoxLayout()
        self.apiKeyLayout.setObjectName("apiKeyLayout")
        self.apiKeyLabel = QLabel(self.centralWidget)
        self.apiKeyLabel.setObjectName("apiKeyLabel")
        self.apiKeyLabel.setText("API Key:")
        self.apiKeyLayout.addWidget(self.apiKeyLabel)
        self.apiKeyLineEdit = QLineEdit(self.centralWidget)
        self.apiKeyLineEdit.setObjectName("apiKeyLineEdit")
        self.apiKeyLayout.addWidget(self.apiKeyLineEdit)
        self.verticalLayout.addLayout(self.apiKeyLayout)

        # Secret Key Layout
        self.secretKeyLayout = QHBoxLayout()
        self.secretKeyLayout.setObjectName("secretKeyLayout")
        self.secretKeyLabel = QLabel(self.centralWidget)
        self.secretKeyLabel.setObjectName("secretKeyLabel")
        self.secretKeyLabel.setText("Secret Key:")
        self.secretKeyLayout.addWidget(self.secretKeyLabel)
        self.secretKeyLineEdit = QLineEdit(self.centralWidget)
        self.secretKeyLineEdit.setObjectName("secretKeyLineEdit")
        self.secretKeyLineEdit.setEchoMode(QLineEdit.Password)
        self.secretKeyLayout.addWidget(self.secretKeyLineEdit)
        self.verticalLayout.addLayout(self.secretKeyLayout)

        # Balance Display Layout
        self.balanceLayout = QHBoxLayout()
        self.balanceLayout.setObjectName("balanceLayout")
        self.balanceTextLabel = QLabel(self.centralWidget)
        self.balanceTextLabel.setObjectName("balanceTextLabel")
        self.balanceTextLabel.setText("Balance (USDT):")
        self.balanceLayout.addWidget(self.balanceTextLabel)

        self.balanceValueLabel = QLabel(self.centralWidget)
        self.balanceValueLabel.setObjectName("balanceValueLabel")
        font = QFont()
        font.setBold(True)
        # font.setPointSize(12) # Optional: make it larger
        self.balanceValueLabel.setFont(font)
        self.balanceValueLabel.setText("N/A")
        self.balanceLayout.addWidget(self.balanceValueLabel)
        self.balanceLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)) # Push value to left
        self.verticalLayout.addLayout(self.balanceLayout)

        # Fetch Button
        self.fetchButtonLayout = QHBoxLayout() # Using a layout to center the button
        self.fetchButtonLayout.setObjectName("fetchButtonLayout")
        self.fetchButtonLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.fetchButton = QPushButton(self.centralWidget)
        self.fetchButton.setObjectName("fetchButton")
        self.fetchButton.setText("Fetch Balance")
        self.fetchButtonLayout.addWidget(self.fetchButton)
        self.fetchButtonLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.verticalLayout.addLayout(self.fetchButtonLayout)

        # Add a spacer at the bottom to push elements upwards
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        # MainWindow.setWindowTitle(_translate("MainWindow", "Binance Balance Checker (PyQt)"))
        # self.apiKeyLabel.setText(_translate("MainWindow", "API Key:"))
        # self.secretKeyLabel.setText(_translate("MainWindow", "Secret Key:"))
        # self.balanceTextLabel.setText(_translate("MainWindow", "Balance (USDT):"))
        # self.balanceValueLabel.setText(_translate("MainWindow", "N/A"))
        # self.fetchButton.setText(_translate("MainWindow", "Fetch Balance"))
        # Note: setText calls are already done during widget creation, retranslateUi is more for internationalization


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

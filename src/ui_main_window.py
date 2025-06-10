from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QApplication, QSpacerItem, QSizePolicy,
                             QTabWidget, QComboBox, QFormLayout, QTextEdit) # Added QTextEdit
from PyQt5.QtCore import QMetaObject, QCoreApplication, QRect
from PyQt5.QtGui import QFont
from .constants import ui_strings # Import ui_strings

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle(ui_strings.WINDOW_TITLE) # Use constant
        MainWindow.resize(500, 550)

        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)

        # Main layout for the central widget (will hold the tab widget)
        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.setObjectName("mainLayout")

        # Tab Widget
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")

        # === Balance Tab ===
        self.balanceTab = QWidget()
        self.balanceTab.setObjectName("balanceTab")
        self.balanceTabLayout = QVBoxLayout(self.balanceTab)
        self.balanceTabLayout.setObjectName("balanceTabLayout")

        # API Key Layout (moved to Balance Tab)
        self.apiKeyLayout = QHBoxLayout()
        self.apiKeyLayout.setObjectName("apiKeyLayout")
        self.apiKeyLabel = QLabel(ui_strings.LABEL_API_KEY) # Use constant
        self.apiKeyLayout.addWidget(self.apiKeyLabel)
        self.apiKeyLineEdit = QLineEdit()
        self.apiKeyLayout.addWidget(self.apiKeyLineEdit)
        self.balanceTabLayout.addLayout(self.apiKeyLayout)

        # Secret Key Layout (moved to Balance Tab)
        self.secretKeyLayout = QHBoxLayout()
        self.secretKeyLayout.setObjectName("secretKeyLayout")
        self.secretKeyLabel = QLabel(ui_strings.LABEL_SECRET_KEY) # Use constant
        self.secretKeyLayout.addWidget(self.secretKeyLabel)
        self.secretKeyLineEdit = QLineEdit()
        self.secretKeyLineEdit.setEchoMode(QLineEdit.Password)
        self.secretKeyLayout.addWidget(self.secretKeyLineEdit)
        self.balanceTabLayout.addLayout(self.secretKeyLayout)

        # Environment ComboBox for Balance
        self.balanceEnvironmentComboBox = QComboBox(self.balanceTab)
        self.balanceEnvironmentComboBox.setObjectName("balanceEnvironmentComboBox")
        self.balanceEnvironmentComboBox.addItems(ui_strings.ENVIRONMENT_CHOICES) # Use constant
        self.balanceEnvLayout = QHBoxLayout()
        self.balanceEnvLabel = QLabel(ui_strings.LABEL_ENVIRONMENT) # Use constant
        self.balanceEnvLayout.addWidget(self.balanceEnvLabel)
        self.balanceEnvLayout.addWidget(self.balanceEnvironmentComboBox)
        self.balanceEnvLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.balanceTabLayout.addLayout(self.balanceEnvLayout)


        # Balance Display Layout (moved to Balance Tab)
        self.balanceDisplayLayout = QHBoxLayout()
        self.balanceDisplayLayout.setObjectName("balanceDisplayLayout")
        self.balanceTextLabel = QLabel(ui_strings.LABEL_BALANCE_USDT) # Use constant
        self.balanceDisplayLayout.addWidget(self.balanceTextLabel)
        self.balanceValueLabel = QLabel(ui_strings.LABEL_BALANCE_DISPLAY_DEFAULT) # Use constant
        font = QFont()
        font.setBold(True)
        self.balanceValueLabel.setFont(font)
        self.balanceDisplayLayout.addWidget(self.balanceValueLabel)
        self.balanceDisplayLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.balanceTabLayout.addLayout(self.balanceDisplayLayout)

        # Fetch Balance Button (moved to Balance Tab)
        self.fetchBalanceButton = QPushButton(ui_strings.BUTTON_FETCH_BALANCE) # Use constant
        self.fetchBalanceButton.setObjectName("fetchBalanceButton")
        # Center button
        self.fetchBalanceButtonLayout = QHBoxLayout()
        self.fetchBalanceButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.fetchBalanceButtonLayout.addWidget(self.fetchBalanceButton)
        self.fetchBalanceButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.balanceTabLayout.addLayout(self.fetchBalanceButtonLayout)

        self.balanceTabLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.tabWidget.addTab(self.balanceTab, ui_strings.TAB_BALANCE) # Use constant

        # === Trade Tab ===
        self.tradeTab = QWidget()
        self.tradeTab.setObjectName("tradeTab")
        self.tradeTabLayout = QVBoxLayout(self.tradeTab) # Main layout for trade tab
        self.tradeTabLayout.setObjectName("tradeTabLayout")

        self.tradeFormLayout = QFormLayout() # Using QFormLayout for inputs
        self.tradeFormLayout.setObjectName("tradeFormLayout")

        # Environment ComboBox for Trade
        self.tradeEnvironmentComboBox = QComboBox()
        self.tradeEnvironmentComboBox.setObjectName("tradeEnvironmentComboBox")
        self.tradeEnvironmentComboBox.addItems(ui_strings.ENVIRONMENT_CHOICES) # Use constant
        self.tradeEnvLabel = QLabel(ui_strings.LABEL_ENVIRONMENT)
        self.tradeFormLayout.addRow(self.tradeEnvLabel, self.tradeEnvironmentComboBox)

        # Symbol Input for Trade tab - distinct from simSymbolComboBox
        self.tradeSymbolLineEdit = QLineEdit()
        self.tradeSymbolLineEdit.setObjectName("tradeSymbolLineEdit")
        self.tradeSymbolLabel = QLabel(ui_strings.LABEL_SYMBOL)
        self.tradeFormLayout.addRow(self.tradeSymbolLabel, self.tradeSymbolLineEdit)

        # Order Type ComboBox
        self.orderTypeComboBox = QComboBox()
        self.orderTypeComboBox.setObjectName("orderTypeComboBox")
        self.orderTypeComboBox.addItems(ui_strings.ORDER_TYPE_CHOICES) # Use constant
        self.tradeOrderTypeLabel = QLabel(ui_strings.LABEL_ORDER_TYPE)
        self.tradeFormLayout.addRow(self.tradeOrderTypeLabel, self.orderTypeComboBox)

        # Side ComboBox
        self.sideComboBox = QComboBox()
        self.sideComboBox.setObjectName("sideComboBox")
        self.sideComboBox.addItems(ui_strings.SIDE_CHOICES) # Use constant
        self.tradeSideLabel = QLabel(ui_strings.LABEL_SIDE)
        self.tradeFormLayout.addRow(self.tradeSideLabel, self.sideComboBox)

        # Amount Input
        self.amountLineEdit = QLineEdit()
        self.amountLineEdit.setObjectName("amountLineEdit")
        self.tradeAmountLabel = QLabel(ui_strings.LABEL_AMOUNT)
        self.tradeFormLayout.addRow(self.tradeAmountLabel, self.amountLineEdit)

        # Price Input
        self.priceLineEdit = QLineEdit()
        self.priceLineEdit.setObjectName("priceLineEdit")
        self.tradePriceLabel = QLabel(ui_strings.LABEL_PRICE_LIMIT_ORDER)
        self.tradeFormLayout.addRow(self.tradePriceLabel, self.priceLineEdit)

        self.tradeTabLayout.addLayout(self.tradeFormLayout)

        # Place Order Button
        self.placeOrderButton = QPushButton(ui_strings.BUTTON_PLACE_ORDER) # Use constant
        self.placeOrderButton.setObjectName("placeOrderButton")
        # Center button
        self.placeOrderButtonLayout = QHBoxLayout()
        self.placeOrderButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.placeOrderButtonLayout.addWidget(self.placeOrderButton)
        self.placeOrderButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.tradeTabLayout.addLayout(self.placeOrderButtonLayout)

        # Trade Status Display
        self.tradeStatusLabel = QLabel(ui_strings.LABEL_STATUS_READY) # Use constant
        self.tradeStatusLabel.setObjectName("tradeStatusLabel")
        self.tradeStatusLabel.setWordWrap(True)
        self.tradeTabLayout.addWidget(self.tradeStatusLabel)

        self.tradeTabLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.tabWidget.addTab(self.tradeTab, ui_strings.TAB_TRADE) # Use constant

        # === Simulation Tab ===
        self.simulationTab = QWidget()
        self.simulationTab.setObjectName("simulationTab")
        self.simulationTabLayout = QVBoxLayout(self.simulationTab)
        self.simulationTabLayout.setObjectName("simulationTabLayout")

        self.simulationFormLayout = QFormLayout()
        self.simulationFormLayout.setObjectName("simulationFormLayout")

        # Symbol ComboBox
        self.simSymbolLabel = QLabel(ui_strings.LABEL_SYMBOL)
        self.simSymbolComboBox = QComboBox()
        self.simSymbolComboBox.setObjectName("simSymbolComboBox")
        self.simSymbolComboBox.addItems(ui_strings.DEFAULT_SYMBOLS)
        self.simulationFormLayout.addRow(self.simSymbolLabel, self.simSymbolComboBox)

        # Environment ComboBox
        self.simEnvironmentLabel = QLabel(ui_strings.LABEL_ENVIRONMENT)
        self.simEnvironmentComboBox = QComboBox()
        self.simEnvironmentComboBox.setObjectName("simEnvironmentComboBox")
        self.simEnvironmentComboBox.addItems(ui_strings.ENVIRONMENT_CHOICES)
        self.simulationFormLayout.addRow(self.simEnvironmentLabel, self.simEnvironmentComboBox)

        # Balance Input
        self.simBalanceLabel = QLabel(ui_strings.LABEL_SIM_BALANCE)
        self.simBalanceLineEdit = QLineEdit()
        self.simBalanceLineEdit.setObjectName("simBalanceLineEdit")
        self.simulationFormLayout.addRow(self.simBalanceLabel, self.simBalanceLineEdit)

        # Prix d'entrée Input
        self.simPrixEntreeLabel = QLabel(ui_strings.LABEL_SIM_PRIX_ENTREE)
        self.simPrixEntreeLineEdit = QLineEdit()
        self.simPrixEntreeLineEdit.setObjectName("simPrixEntreeLineEdit")
        self.simulationFormLayout.addRow(self.simPrixEntreeLabel, self.simPrixEntreeLineEdit)

        # Prix catastrophique Input
        self.simPrixCatastrophiqueLabel = QLabel(ui_strings.LABEL_SIM_PRIX_CATASTROPHIQUE)
        self.simPrixCatastrophiqueLineEdit = QLineEdit()
        self.simPrixCatastrophiqueLineEdit.setObjectName("simPrixCatastrophiqueLineEdit")
        self.simulationFormLayout.addRow(self.simPrixCatastrophiqueLabel, self.simPrixCatastrophiqueLineEdit)

        # Pourcentage de drop Input
        self.simDropPercentLabel = QLabel(ui_strings.LABEL_SIM_DROP_PERCENT)
        self.simDropPercentLineEdit = QLineEdit()
        self.simDropPercentLineEdit.setObjectName("simDropPercentLineEdit")
        self.simulationFormLayout.addRow(self.simDropPercentLabel, self.simDropPercentLineEdit)

        self.simulationTabLayout.addLayout(self.simulationFormLayout)

        # Calculer Button
        self.simCalculerButton = QPushButton(ui_strings.BUTTON_CALCULATE_SIMULATION)
        self.simCalculerButton.setObjectName("simCalculerButton")
        # Center button
        self.simCalculerButtonLayout = QHBoxLayout()
        self.simCalculerButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.simCalculerButtonLayout.addWidget(self.simCalculerButton)
        self.simCalculerButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.simulationTabLayout.addLayout(self.simCalculerButtonLayout)


        # Results Display Area
        self.simResultsTextEdit = QTextEdit()
        self.simResultsTextEdit.setObjectName("simResultsTextEdit")
        self.simResultsTextEdit.setReadOnly(True)
        self.simulationTabLayout.addWidget(self.simResultsTextEdit)
        self.simulationTabLayout.setStretchFactor(self.simResultsTextEdit, 1)

        self.tabWidget.addTab(self.simulationTab, ui_strings.TAB_SIMULATION_DCA) # Use constant

        # Add TabWidget to the main layout of the central widget
        self.mainLayout.addWidget(self.tabWidget)

        self.retranslateUi(MainWindow)
        # QMetaObject.connectSlotsByName(MainWindow) # Usually called by uic or if using Qt Designer setup

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        # MainWindow.setWindowTitle(_translate("MainWindow", "Binance Balance & Trade Tool (PyQt)"))
        # self.apiKeyLabel.setText(_translate("MainWindow", "API Key:"))
        # ... (texts for other widgets are set during creation)
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.balanceTab), _translate("MainWindow", "Balance"))
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.tradeTab), _translate("MainWindow", "Trade"))
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.simulationTab), _translate("MainWindow", "Simulation DCA"))
        # Note: setText calls are mostly done during widget creation. Retranslate is for language changes.


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

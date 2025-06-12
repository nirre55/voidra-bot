from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QApplication, QSpacerItem, QSizePolicy,
                             QTabWidget, QComboBox, QFormLayout, QTextEdit, QCheckBox)
from PyQt5.QtCore import QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont
from .constants import ui_strings

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle(ui_strings.WINDOW_TITLE)
        MainWindow.resize(500, 550)

        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.setObjectName("mainLayout")

        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")

        # === Config Tab (Previously Balance Tab) ===
        self.configTab = QWidget()
        self.configTab.setObjectName("configTab")
        self.configTabLayout = QVBoxLayout(self.configTab)
        self.configTabLayout.setObjectName("configTabLayout")

        # API Key Layout
        self.apiKeyLayout = QHBoxLayout()
        self.apiKeyLayout.setObjectName("apiKeyLayout")
        self.apiKeyLabel = QLabel(ui_strings.LABEL_API_KEY, self.configTab)
        self.apiKeyLayout.addWidget(self.apiKeyLabel)
        self.apiKeyLineEdit = QLineEdit(self.configTab)
        self.apiKeyLineEdit.setObjectName("apiKeyLineEdit")
        self.apiKeyLayout.addWidget(self.apiKeyLineEdit)
        self.configTabLayout.addLayout(self.apiKeyLayout)

        # Secret Key Layout
        self.secretKeyLayout = QHBoxLayout()
        self.secretKeyLayout.setObjectName("secretKeyLayout")
        self.secretKeyLabel = QLabel(ui_strings.LABEL_SECRET_KEY, self.configTab)
        self.secretKeyLayout.addWidget(self.secretKeyLabel)
        self.secretKeyLineEdit = QLineEdit(self.configTab)
        self.secretKeyLineEdit.setObjectName("secretKeyLineEdit")
        self.secretKeyLineEdit.setEchoMode(QLineEdit.Password)
        self.secretKeyLayout.addWidget(self.secretKeyLineEdit)
        self.configTabLayout.addLayout(self.secretKeyLayout)

        # Save API Keys CheckBox
        self.saveApiKeysCheckBox = QCheckBox(ui_strings.CHECKBOX_SAVE_API_KEYS, self.configTab)
        self.saveApiKeysCheckBox.setObjectName("saveApiKeysCheckBox")
        self.configTabLayout.addWidget(self.saveApiKeysCheckBox)

        # Global Environment ComboBox (for API Keys and Balance)
        self.globalEnvironmentComboBox = QComboBox(self.configTab)
        self.globalEnvironmentComboBox.setObjectName("globalEnvironmentComboBox")
        self.globalEnvironmentComboBox.addItems(ui_strings.ENVIRONMENT_CHOICES)

        self.globalEnvLayout = QHBoxLayout()
        self.globalEnvLabel = QLabel(ui_strings.LABEL_ENVIRONMENT, self.configTab)
        self.globalEnvLayout.addWidget(self.globalEnvLabel)
        self.globalEnvLayout.addWidget(self.globalEnvironmentComboBox)
        self.globalEnvLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.configTabLayout.addLayout(self.globalEnvLayout)

        # Balance Display Layout
        self.balanceDisplayLayout = QHBoxLayout()
        self.balanceDisplayLayout.setObjectName("balanceDisplayLayout")
        self.balanceTextLabel = QLabel(ui_strings.LABEL_BALANCE_USDT, self.configTab)
        self.balanceDisplayLayout.addWidget(self.balanceTextLabel)
        self.balanceValueLabel = QLabel(ui_strings.LABEL_BALANCE_DISPLAY_DEFAULT, self.configTab)
        font = QFont()
        font.setBold(True)
        self.balanceValueLabel.setFont(font)
        self.balanceDisplayLayout.addWidget(self.balanceValueLabel)
        self.balanceDisplayLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.configTabLayout.addLayout(self.balanceDisplayLayout)

        # Fetch Balance Button
        self.fetchBalanceButton = QPushButton(ui_strings.BUTTON_FETCH_BALANCE, self.configTab)
        self.fetchBalanceButton.setObjectName("fetchBalanceButton")
        self.fetchBalanceButtonLayout = QHBoxLayout()
        self.fetchBalanceButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.fetchBalanceButtonLayout.addWidget(self.fetchBalanceButton)
        self.fetchBalanceButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.configTabLayout.addLayout(self.fetchBalanceButtonLayout)

        self.configTabLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.tabWidget.addTab(self.configTab, ui_strings.TAB_CONFIG) # Use new constant for tab name

        # === Trade Tab ===
        self.tradeTab = QWidget()
        self.tradeTab.setObjectName("tradeTab")
        self.tradeTabLayout = QVBoxLayout(self.tradeTab)
        self.tradeTabLayout.setObjectName("tradeTabLayout")

        self.tradeFormLayout = QFormLayout()
        self.tradeFormLayout.setObjectName("tradeFormLayout")

        # Symbol Input for Trade tab
        self.tradeSymbolLineEdit = QLineEdit(self.tradeTab)
        self.tradeSymbolLineEdit.setObjectName("tradeSymbolLineEdit") # Corrected objectName
        self.tradeSymbolLabel = QLabel(ui_strings.LABEL_SYMBOL, self.tradeTab)
        self.tradeFormLayout.addRow(self.tradeSymbolLabel, self.tradeSymbolLineEdit)

        # Order Type ComboBox
        self.orderTypeComboBox = QComboBox(self.tradeTab)
        self.orderTypeComboBox.setObjectName("orderTypeComboBox")
        self.orderTypeComboBox.addItems(ui_strings.ORDER_TYPE_CHOICES)
        self.tradeOrderTypeLabel = QLabel(ui_strings.LABEL_ORDER_TYPE, self.tradeTab)
        self.tradeFormLayout.addRow(self.tradeOrderTypeLabel, self.orderTypeComboBox)

        # Side ComboBox
        self.sideComboBox = QComboBox(self.tradeTab)
        self.sideComboBox.setObjectName("sideComboBox")
        self.sideComboBox.addItems(ui_strings.SIDE_CHOICES)
        self.tradeSideLabel = QLabel(ui_strings.LABEL_SIDE, self.tradeTab)
        self.tradeFormLayout.addRow(self.tradeSideLabel, self.sideComboBox)

        # Amount Input
        self.amountLineEdit = QLineEdit(self.tradeTab)
        self.amountLineEdit.setObjectName("amountLineEdit")
        self.tradeAmountLabel = QLabel(ui_strings.LABEL_AMOUNT, self.tradeTab)
        self.tradeFormLayout.addRow(self.tradeAmountLabel, self.amountLineEdit)

        # Price Input
        self.priceLineEdit = QLineEdit(self.tradeTab)
        self.priceLineEdit.setObjectName("priceLineEdit")
        self.tradePriceLabel = QLabel(ui_strings.LABEL_PRICE_LIMIT_ORDER, self.tradeTab)
        self.tradeFormLayout.addRow(self.tradePriceLabel, self.priceLineEdit)

        self.tradeTabLayout.addLayout(self.tradeFormLayout)

        # Place Order Button
        self.placeOrderButton = QPushButton(ui_strings.BUTTON_PLACE_ORDER, self.tradeTab)
        self.placeOrderButton.setObjectName("placeOrderButton")
        self.placeOrderButtonLayout = QHBoxLayout()
        self.placeOrderButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.placeOrderButtonLayout.addWidget(self.placeOrderButton)
        self.placeOrderButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.tradeTabLayout.addLayout(self.placeOrderButtonLayout)

        # Trade Status Display
        self.tradeStatusLabel = QLabel(ui_strings.LABEL_STATUS_READY, self.tradeTab)
        self.tradeStatusLabel.setObjectName("tradeStatusLabel")
        self.tradeStatusLabel.setWordWrap(True)
        self.tradeTabLayout.addWidget(self.tradeStatusLabel)

        self.tradeTabLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.tabWidget.addTab(self.tradeTab, ui_strings.TAB_TRADE)

        # === Simulation Tab ===
        self.simulationTab = QWidget()
        self.simulationTab.setObjectName("simulationTab")
        self.simulationTabLayout = QVBoxLayout(self.simulationTab)
        self.simulationTabLayout.setObjectName("simulationTabLayout")

        self.simulationFormLayout = QFormLayout()
        self.simulationFormLayout.setObjectName("simulationFormLayout")

        # Symbol ComboBox for Simulation
        self.simSymbolLabel = QLabel(ui_strings.LABEL_SYMBOL, self.simulationTab)
        self.simSymbolComboBox = QComboBox(self.simulationTab)
        self.simSymbolComboBox.setObjectName("simSymbolComboBox")
        self.simSymbolComboBox.addItems(ui_strings.DEFAULT_SYMBOLS)
        self.simulationFormLayout.addRow(self.simSymbolLabel, self.simSymbolComboBox)

        # Balance Input
        self.simBalanceLabel = QLabel(ui_strings.LABEL_SIM_BALANCE, self.simulationTab)
        self.simBalanceLineEdit = QLineEdit(self.simulationTab)
        self.simBalanceLineEdit.setObjectName("simBalanceLineEdit")
        self.simulationFormLayout.addRow(self.simBalanceLabel, self.simBalanceLineEdit)

        # Prix d'entrée Input
        self.simPrixEntreeLabel = QLabel(ui_strings.LABEL_SIM_PRIX_ENTREE, self.simulationTab)
        self.simPrixEntreeLineEdit = QLineEdit(self.simulationTab)
        self.simPrixEntreeLineEdit.setObjectName("simPrixEntreeLineEdit")
        self.simulationFormLayout.addRow(self.simPrixEntreeLabel, self.simPrixEntreeLineEdit)

        # Prix catastrophique Input
        self.simPrixCatastrophiqueLabel = QLabel(ui_strings.LABEL_SIM_PRIX_CATASTROPHIQUE, self.simulationTab)
        self.simPrixCatastrophiqueLineEdit = QLineEdit(self.simulationTab)
        self.simPrixCatastrophiqueLineEdit.setObjectName("simPrixCatastrophiqueLineEdit")
        self.simulationFormLayout.addRow(self.simPrixCatastrophiqueLabel, self.simPrixCatastrophiqueLineEdit)

        # Pourcentage de drop Input
        self.simDropPercentLabel = QLabel(ui_strings.LABEL_SIM_DROP_PERCENT, self.simulationTab)
        self.simDropPercentLineEdit = QLineEdit(self.simulationTab)
        self.simDropPercentLineEdit.setObjectName("simDropPercentLineEdit")
        self.simulationFormLayout.addRow(self.simDropPercentLabel, self.simDropPercentLineEdit)

        self.simulationTabLayout.addLayout(self.simulationFormLayout)

        # Calculer Button
        self.simCalculerButton = QPushButton(ui_strings.BUTTON_CALCULATE_SIMULATION, self.simulationTab)
        self.simCalculerButton.setObjectName("simCalculerButton")
        self.simCalculerButtonLayout = QHBoxLayout()
        self.simCalculerButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.simCalculerButtonLayout.addWidget(self.simCalculerButton)
        self.simCalculerButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.simulationTabLayout.addLayout(self.simCalculerButtonLayout)

        # Results Display Area
        self.simResultsTextEdit = QTextEdit(self.simulationTab)
        self.simResultsTextEdit.setObjectName("simResultsTextEdit")
        self.simResultsTextEdit.setReadOnly(True)
        self.simulationTabLayout.addWidget(self.simResultsTextEdit)
        self.simulationTabLayout.setStretchFactor(self.simResultsTextEdit, 1)

        self.tabWidget.addTab(self.simulationTab, ui_strings.TAB_SIMULATION_DCA)

        # === DCA Orders Tab ===
        self.dcaOrdersTab = QWidget()
        self.dcaOrdersTab.setObjectName("dcaOrdersTab")
        self.dcaOrdersTabLayout = QVBoxLayout(self.dcaOrdersTab)
        self.dcaOrdersTabLayout.setObjectName("dcaOrdersTabLayout")

        # Symbol Display Layout
        self.dcaSymbolDisplayLayout = QHBoxLayout()
        self.dcaSymbolDisplayLayout.setObjectName("dcaSymbolDisplayLayout")
        self.dcaSymbolDisplayLabel = QLabel("Symbol:", self.dcaOrdersTab) # Placeholder, use ui_strings later
        self.dcaSymbolDisplayLayout.addWidget(self.dcaSymbolDisplayLabel)
        self.dcaSymbolValueLabel = QLabel("N/A", self.dcaOrdersTab) # Placeholder, to be updated
        self.dcaSymbolDisplayLayout.addWidget(self.dcaSymbolValueLabel)
        self.dcaSymbolDisplayLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.dcaOrdersTabLayout.addLayout(self.dcaSymbolDisplayLayout)

        # Load Data Button
        self.dcaLoadDataButton = QPushButton(ui_strings.BUTTON_LOAD_DCA_DATA, self.dcaOrdersTab) # Text from ui_strings
        self.dcaLoadDataButton.setObjectName("dcaLoadDataButton")
        # Center the button - create a layout for it
        self.dcaLoadDataButtonLayout = QHBoxLayout()
        self.dcaLoadDataButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.dcaLoadDataButtonLayout.addWidget(self.dcaLoadDataButton)
        self.dcaLoadDataButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.dcaOrdersTabLayout.addLayout(self.dcaLoadDataButtonLayout)

        # Simulation Data Display
        self.dcaSimResultsTextEdit = QTextEdit(self.dcaOrdersTab)
        self.dcaSimResultsTextEdit.setObjectName("dcaSimResultsTextEdit")
        self.dcaSimResultsTextEdit.setReadOnly(True)
        self.dcaOrdersTabLayout.addWidget(self.dcaSimResultsTextEdit)

        # Place DCA Orders Button
        self.dcaPlaceOrdersButton = QPushButton("Place DCA Orders", self.dcaOrdersTab) # Placeholder, use ui_strings later
        self.dcaPlaceOrdersButton.setObjectName("dcaPlaceOrdersButton")
        self.dcaPlaceOrdersButton.setEnabled(False)
        self.dcaPlaceOrdersButtonLayout = QHBoxLayout()
        self.dcaPlaceOrdersButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.dcaPlaceOrdersButtonLayout.addWidget(self.dcaPlaceOrdersButton)
        self.dcaPlaceOrdersButtonLayout.addSpacerItem(QSpacerItem(40,20,QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.dcaOrdersTabLayout.addLayout(self.dcaPlaceOrdersButtonLayout)

        # Status Label
        self.dcaStatusLabel = QLabel("Status: Ready", self.dcaOrdersTab) # Placeholder, use ui_strings later
        self.dcaStatusLabel.setObjectName("dcaStatusLabel")
        self.dcaStatusLabel.setWordWrap(True)
        self.dcaOrdersTabLayout.addWidget(self.dcaStatusLabel)

        self.dcaOrdersTabLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.tabWidget.addTab(self.dcaOrdersTab, "DCA Orders") # Placeholder, use ui_strings later

        self.mainLayout.addWidget(self.tabWidget)

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        # _translate = QCoreApplication.translate # Not strictly needed if all texts are set by constants
        # Texts are set directly using ui_strings in setupUi.
        # If internationalization with QTranslator is added later, this method would be used.
        # For now, ensure the new tab title is also set via ui_strings or directly if not yet in constants
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.dcaOrdersTab), _translate("MainWindow", "DCA Orders")) # Example
        pass



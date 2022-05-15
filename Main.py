from select import select
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem, QDialog
import sys
from Cassandra import Cassandra
from enum import Enum


class Alert(QDialog):
    def __init__(self):
        super(Alert, self).__init__()
        uic.loadUi("Alert.ui", self)

        self.closeBtn.clicked.connect(self.closeThis)

    def closeThis(self):
        self.close()

class TambahTable(QDialog):
    window_closed = pyqtSignal(str)
    def __init__(self):
        super(TambahTable, self).__init__()
        uic.loadUi("TambahTable.ui", self)
        self.setWindowTitle("Tambah Table")
        self.OkCancelButton.accepted.connect(self.createTable)
        self.OkCancelButton.rejected.connect(self.button_rejected)

        self.query_table.setWordWrapMode(False)

    def closeEvent(self, event):
        event.accept()

    def createTable(self):
        query = self.query_table.toPlainText()
        self.window_closed.emit(query)
        self.close()
    
    def button_rejected(self):
        self.close()

class TambahKeyspace(QDialog):
    window_closed = pyqtSignal(str)
    def __init__(self):
        super(TambahKeyspace, self).__init__()
        uic.loadUi("TambahKeyspace.ui", self)
        self.setWindowTitle("Tambah Keyspace")

        self.OkCancelButton.accepted.connect(self.createKeyspace)
        self.OkCancelButton.rejected.connect(self.button_rejected)


        self.tambahKeyspace_checkbox.stateChanged.connect(self.checkBox_state)
        self.query_keyspace.setWordWrapMode(False)

    def closeEvent(self, event):
        # self.window_closed.emit("aa")
        event.accept()

    def createKeyspace(self):
        isChecked = self.tambahKeyspace_checkbox.isChecked()
        if isChecked == True:
            query = self.query_keyspace.toPlainText()
        else:
            nama_keyspace = self.nama_keyspace.toPlainText()
            class_keyspace = self.class_keyspace.toPlainText()
            replication_factor = int(self.replication_factor.toPlainText())

            query = "create keyspace %s with replication = {'class': '%s', 'replication_factor': %d};" % (nama_keyspace, class_keyspace, replication_factor)
        self.window_closed.emit(query)
        self.close()

    def button_rejected(self):
        self.close()

    def checkBox_state(self):
        isChecked = self.tambahKeyspace_checkbox.isChecked()
        if isChecked == True:
            self.nama_keyspace.setDisabled(True)
            self.nama_keyspace.setPlainText("")
            self.class_keyspace.setDisabled(True)
            self.class_keyspace.setPlainText("")
            self.replication_factor.setDisabled(True)
            self.replication_factor.setPlainText("")
            self.query_keyspace.setDisabled(False)
        else:
            self.nama_keyspace.setDisabled(False)
            self.class_keyspace.setDisabled(False)
            self.replication_factor.setDisabled(False)
            self.query_keyspace.setDisabled(True)
            self.query_keyspace.setPlainText("")

class TambahEditData(QDialog):
    window_closed = pyqtSignal(str, str)
    def __init__(self):
        super(TambahEditData, self).__init__()
        uic.loadUi("TambahEditData.ui", self)

        self.columns = ""
        self.inputTextColumns = {}
        self.isTambahData = ""
        self.keyspace_name = ""
        self.table_name = ""
        self.data = ""

    def closeEvent(self, event):
        # self.window_closed.emit("aa")
        event.accept()

    def generateInput(self):
        font = QtGui.QFont()
        
        # self.label_info = QtWidgets.QLabel(self)
        # self.label_info.setGeometry(QtCore.QRect(30, 20, 411, 21))
        # font.setPointSize(14)
        # self.label_info.setFont(font)
        # self.label_info.setObjectName("label_info")

        x_value, y_value = 50,50
        for col in self.columns:
            self.inputTextColumns[col] = QtWidgets.QPlainTextEdit(self)
            self.inputTextColumns[col].setGeometry(QtCore.QRect(x_value, y_value,391, 31))
            font.setPointSize(12)
            # self.inputTextColumns[col].setPlaceholderText(col)
            self.inputTextColumns[col].setFont(font)
            self.inputTextColumns[col].setObjectName("input_"+col)
            y_value +=40

        y_value += 10

        self.OkCancelButton = QtWidgets.QDialogButtonBox(self)
        self.OkCancelButton.setGeometry(QtCore.QRect(160, y_value, 161, 31))
        font.setPointSize(11)
        self.OkCancelButton.setFont(font)
        self.OkCancelButton.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.OkCancelButton.setObjectName("OkCancelButton")
        self.OkCancelButton.accepted.connect(self.tambah_data)
        self.OkCancelButton.rejected.connect(self.cancel)
        
        self.ubah_btn = QtWidgets.QPushButton(self)
        self.ubah_btn.setGeometry(QtCore.QRect(100, y_value, 81, 31))
        font.setPointSize(11)
        self.ubah_btn.setFont(font)
        self.ubah_btn.setObjectName("ubah_btn")
        self.ubah_btn.setText("Ubah")
        self.ubah_btn.clicked.connect(self.ubah_data)

        self.hapus_btn = QtWidgets.QPushButton(self)
        self.hapus_btn.setGeometry(QtCore.QRect(190, y_value, 81, 31))
        font.setPointSize(11)
        self.hapus_btn.setFont(font)
        self.hapus_btn.setObjectName("hapus_btn")
        self.hapus_btn.setText("Hapus")
        self.hapus_btn.clicked.connect(self.hapus_data)

        self.batal_btn = QtWidgets.QPushButton(self)
        self.batal_btn.setGeometry(QtCore.QRect(280, y_value, 81, 31))
        font.setPointSize(11)
        self.batal_btn.setFont(font)
        self.batal_btn.setObjectName("batal_btn")
        self.batal_btn.setText("Batal")
        self.batal_btn.clicked.connect(self.cancel)

        if self.isTambahData:
            for col in self.columns:
                self.inputTextColumns[col].setPlaceholderText(col)
            self.OkCancelButton.show()
            self.ubah_btn.hide()
            self.batal_btn.hide()
            self.hapus_btn.hide()

        elif not self.isTambahData:
            index = 0
            for col in self.columns:
                self.inputTextColumns[col].setPlainText(self.data[index])
                if index == 0:
                    self.inputTextColumns[col].setDisabled(True)
                index += 1
            self.OkCancelButton.hide()
            self.ubah_btn.show()
            self.batal_btn.show()
            self.hapus_btn.show()

        self.resize(461, y_value+41)
        self.keyspace_and_table.setText(f"Keyspace: {self.keyspace_name}, Table: {self.table_name}")

    def tambah_data(self):
        columns = tuple(self.inputTextColumns.keys())
        values = tuple([self.inputTextColumns[col].toPlainText() for col in self.columns])
        col = "("
        for i in columns:
            col += i + ","
        col = col[:-1] + ")"
        query = f"insert into {self.keyspace_name}.{self.table_name} {col} values {values};"
        self.window_closed.emit(query, "tambah")
        self.close()

    def cancel(self):
        self.close()
    
    def ubah_data(self):
        columns = list(self.inputTextColumns.keys())
        primary_key = columns[0]
        new_columns = columns[1:]
        values = [self.inputTextColumns[col].toPlainText() for col in self.columns]
        primary_value = values[0]
        new_values = values[1:]
        sett = ""
        for i in range(len(new_columns)):
            sett += f"{new_columns[i]} = '{new_values[i]}',"
        sett = sett[:-1]
        query = f"update {self.keyspace_name}.{self.table_name} set {sett} where {primary_key} = '{primary_value}';"
        self.window_closed.emit(query, "ubah")
        self.close()

    def hapus_data(self):
        columns = list(self.inputTextColumns.keys())
        primary_key = columns[0]
        values = [self.inputTextColumns[col].toPlainText() for col in self.columns]
        primary_value = values[0]
        query = f"delete from {self.keyspace_name}.{self.table_name} where {primary_key} = '{primary_value}';"
        self.window_closed.emit(query, "hapus")
        self.close()

class Hapus(QDialog):
    class Pilihan(Enum):
            KEYSPACE = "KEYSPACE"
            TABLE = "TABLE"
    window_closed = pyqtSignal(str, str)
    def __init__(self):
        super(Hapus, self).__init__()
        uic.loadUi("Hapus.ui", self)
        self.setWindowTitle("Konfirmasi Hapus")

        self.nama = ""
        self.keyspace = ""
        self.yang_dihapus = ""

        self.OkCancelButtonHapus.accepted.connect(self.hapus)
        self.OkCancelButtonHapus.rejected.connect(self.button_rejected)

    def hapus(self):
        if self.yang_dihapus == Hapus.Pilihan.KEYSPACE.value:
            query = f"DROP {self.yang_dihapus} IF EXISTS {self.nama}"
        elif self.yang_dihapus == Hapus.Pilihan.TABLE.value:
            query = f"DROP TABLE IF EXISTS  {self.keyspace}.{self.nama}"
        self.window_closed.emit(query, self.yang_dihapus)
        self.close()

    def button_rejected(self):
        self.close()

class Filter(QDialog):
    window_closed = pyqtSignal(str, list)
    def __init__(self):
        super(Filter, self).__init__()
        uic.loadUi("Filter.ui", self)
        self.setWindowTitle("Filter data")

        self.columns = ""
        self.keyspace_name = ""
        self.table_name = ""
        self.checkBoxColumns = {}
        self.inputTextColumns = {}

    def generateCheckBoxAndInput(self):
        x_value, y_value = 60, 50
        font = QtGui.QFont()
        font.setPointSize(14)

        self.label_select = QtWidgets.QLabel(self)
        self.label_select.setGeometry(QtCore.QRect(30, 20, 61, 21))
        self.label_select.setObjectName("label_select")
        self.label_select.setText("SELECT: ")
        self.label_select.setFont(font)

        for col in self.columns:
            self.checkBoxColumns[col] = QtWidgets.QCheckBox(self)
            self.checkBoxColumns[col].setGeometry(QtCore.QRect(x_value, y_value,91, 16))
            font.setPointSize(12)
            self.checkBoxColumns[col].setFont(font)
            self.checkBoxColumns[col].setObjectName("select_"+col)
            self.checkBoxColumns[col].setText(col)
            # self.test[col].stateChanged.connect(self.checkBox_state)
            # self.checkbox = QtWidgets.QCheckBox(self)
            # self.checkbox.setGeometry(QtCore.QRect(x_value, y_value,91, 16))
            # font.setPointSize(12)
            # self.checkbox.setFont(font)
            # self.checkbox.setObjectName("select_"+col)
            # self.checkbox.setText(col)
            # self.checkbox.stateChanged.connect(self.checkBox_state)
            y_value += 30
        
        y_value += 10

        self.label_where = QtWidgets.QLabel(self)
        self.label_where.setGeometry(QtCore.QRect(30, y_value, 61, 21))
        self.label_where.setObjectName("label_where")
        self.label_where.setText("WHERE: ")
        font.setPointSize(14)
        self.label_where.setFont(font)

        y_value += 30
        for col in self.columns:
            self.inputTextColumns[col] = QtWidgets.QPlainTextEdit(self)
            self.inputTextColumns[col].setGeometry(QtCore.QRect(x_value, y_value,271, 31))
            font.setPointSize(12)
            self.inputTextColumns[col].setPlaceholderText(col)
            self.inputTextColumns[col].setFont(font)
            self.inputTextColumns[col].setObjectName("where_"+col)
            # self.plainTextEdit = QtWidgets.QPlainTextEdit(self)
            # self.plainTextEdit.setGeometry(QtCore.QRect(x_value, y_value,271, 31))
            # font.setPointSize(12)
            # self.plainTextEdit.setPlaceholderText(col)
            # self.plainTextEdit.setFont(font)
            # self.plainTextEdit.setObjectName("where_"+col)
            y_value += 40

        y_value += 10
        self.cari_button = QtWidgets.QPushButton(self)
        self.cari_button.setGeometry(QtCore.QRect(240, y_value, 81, 31))
        font.setPointSize(12)
        self.cari_button.setFont(font)
        self.cari_button.setObjectName("cari_button")
        self.cari_button.setText("Cari")
        self.cari_button.clicked.connect(self.cari)

        self.resize(340, y_value+ 45)

    def cari(self):
        select = ""
        where = ""
        select_list = []
        for col in self.columns:
            if self.checkBoxColumns[col].isChecked():
                select += col + ","
                select_list.append(col)
            inputan = self.inputTextColumns[col].toPlainText()
            if inputan != "":
                where += f"{col} = '{inputan}' and "

        select = select[:-1]
        where = where[:-5]
        if where != "":
            query = f"select {select} from {self.keyspace_name}.{self.table_name} where {where} allow filtering;"
        elif where == "":
            query = f"select {select} from {self.keyspace_name}.{self.table_name} allow filtering;"

        self.window_closed.emit(query, select_list)
        self.close()
            # print(self.inputTextColumns[col].toPlainText())
            # print(self.checkBoxColumns[col].isChecked())
        # print("===")
    # def checkBox_state(self):
    #     print(self.test["id"].isChecked())

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('GUI.ui', self)

        self.keyspace_name = ""
        self.table_name = ""

        self.cassandra = Cassandra()
        self.tambahKeyspace = TambahKeyspace()
        self.hapusWindow = Hapus()
        self.alert = Alert()
        self.tambahTable = TambahTable()
        self.filter = Filter()
        self.tambahEditData = TambahEditData()
        
        self.tambahKeyspace.window_closed.connect(self.tambah_keyspace_closed)
        self.tambahTable.window_closed.connect(self.tambah_table_closed)
        self.hapusWindow.window_closed.connect(self.hapus)
        self.tambahEditData.window_closed.connect(self.tambah_and_edit)
        self.filter.window_closed.connect(self.hasil_filter)
        self.setWindowTitle("Mini Project 3a")

        self.connect_button.clicked.connect(self.connect)
        self.tambah_keyspace_button.clicked.connect(self.tambahKeyspace.exec_)
        self.tambah_table_button.clicked.connect(self.tambahTable.exec_)
        self.filter_table_data.clicked.connect(self.filter_data)
        self.tambah_table_data.clicked.connect(self.tambah_data)
        
        self.hapus_keyspace_btn.clicked.connect(self.hapus_keyspace)
        self.hapus_table_btn.clicked.connect(self.hapus_table)
        self.refresh_table_data.clicked.connect(lambda x: self.show_data(self.keyspace_name, self.table_name))

    def connect(self):
        self.reset_Qtables(all = True)
        self.alert.alert_text.setText("Connecting ...")
        self.connect_result.setText("Connecting ...")
        conn = self.cassandra.connect(self.public_ip.toPlainText())
        self.connect_result.setText(conn)
        self.connect_result.adjustSize()
        try:
            self.show_keyspaces()
        except:
            # total = 8
            # self.table_keyspace.cellClicked.connect(self.cell_was_clicked)
            # self.table_keyspace.cellDoubleClicked.connect(self.test)
            # self.table_keyspace.setRowCount(total)
            # for i in range(total):
            #     # self.table_keyspace.setItem(i, 0, QTableWidgetItem(str(keyspace_list[i])))
            #     self.table_keyspace.setItem(i, 0, QTableWidgetItem(str("AAAAa")))
            pass

    def show_keyspaces(self):
        self.reset_Qtables(keyspace_table=True)
        keyspace_list = [i.keyspace_name for i in self.cassandra.get_keyspaces()]
        total = len(keyspace_list)
        self.table_keyspace.cellClicked.connect(self.cell_was_clicked)
        # self.table_keyspace.cellDoubleClicked.connect(self.test)
        # self.hapus_keyspace_btn.clicked.connect(lambda x: self.hapus_keyspace(self.keyspace_name))
        # self.hapus_keyspace_btn.clicked.connect(self.hapus_keyspace)
        self.table_keyspace.setRowCount(total)
        for i in range(total):
            self.table_keyspace.setItem(i, 0, QTableWidgetItem(str(keyspace_list[i])))
            # self.table_keyspace.setItem(i, 0, QTableWidgetItem(str("AAAAa")))

    def hapus_keyspace(self):
        if self.keyspace_name =="":
            self.alert.setWindowTitle("Gagal")
            self.alert.alert_text.setText("Pilih keyspacenya dulu!")
            self.alert.exec_()
        else:
            self.alert.setWindowTitle("Berhasil")
            self.hapusWindow.yang_dihapus = self.hapusWindow.Pilihan.KEYSPACE.value
            self.hapusWindow.nama = self.keyspace_name
            self.hapusWindow.hapus_text.setText(f"Hapus keyspace {self.keyspace_name}")
            self.hapusWindow.exec_()

    def hapus_table(self):
        if self.keyspace_name =="":
            self.alert.setWindowTitle("Gagal")
            self.alert.alert_text.setText("Pilih keyspacenya dulu!")
            self.alert.exec_()
        elif self.table_name =="":
            self.alert.setWindowTitle("Gagal")
            self.alert.alert_text.setText("Pilih table dulu!")
            self.alert.exec_()
        else:
            self.alert.setWindowTitle("Berhasil")
            self.hapusWindow.keyspace = self.keyspace_name
            self.hapusWindow.yang_dihapus = self.hapusWindow.Pilihan.TABLE.value
            self.hapusWindow.nama = self.table_name
            self.hapusWindow.hapus_text.setText(f"Hapus table {self.table_name}")
            self.hapusWindow.exec_()

    def hapus(self, query, yang_dihapus):
        self.cassandra.execute_query(query)
        if yang_dihapus == self.hapusWindow.Pilihan.KEYSPACE.value:
            self.reset_Qtables(keyspace_table= True)
            self.show_keyspaces()
        elif yang_dihapus == self.hapusWindow.Pilihan.TABLE.value:
            self.reset_Qtables(table_table = True)
            self.show_tables(self.keyspace_name)
        self.alert.alert_text.setText(f"{yang_dihapus} berhasil dihapus!")
        self.alert.exec_()

    def test(self, row, column):
        self.tambahKeyspace.exec_()

    def cell_was_clicked(self, row, column):
        self.reset_Qtables(table_table=True)
        self.keyspace_name = self.table_keyspace.item(row, column).text()
        self.cassandra.keyspace_name = self.keyspace_name
        self.keyspace_table_name.setText(f"Keyspace: {self.keyspace_name}")
        self.show_tables(self.keyspace_name)
        # table_list = [i.table_name for i in self.cassandra.get_tables(self.keyspace_name)]
        # total = len(table_list)
        # self.table_table.setRowCount(total)
        # for i in range (total):
        #     self.table_table.setItem(i,0, QTableWidgetItem(str(table_list[i])))
    
    def show_tables(self, keyspace):
        table_list = [i.table_name for i in self.cassandra.get_tables(keyspace)]
        total = len(table_list)
        self.table_table.cellClicked.connect(self.table_clicked)
        self.table_table.setRowCount(total)
        for i in range (total):
            self.table_table.setItem(i,0, QTableWidgetItem(str(table_list[i])))

    def table_clicked(self, row, column):
        self.table_name = self.table_table.item(row, column).text()
        self.cassandra.table_name = self.table_name
        self.keyspace_and_table.setText(f"Keyspace: {self.keyspace_name}, table: {self.table_name}")
        self.show_data(self.keyspace_name, self.table_name)

    def show_data(self, keyspace, table):
        temp_columns_name = [[i.column_name, i.kind] for i in self.cassandra.get_columns_name(keyspace, table)]
        columns_name = []
        for col in temp_columns_name:
            if col[1] != "partition_key":
                columns_name.append(col[0])
            elif col[1] == "partition_key":
                columns_name.insert(0, col[0])
        
        self.table_data.setColumnCount(len(columns_name))
        self.table_data.setHorizontalHeaderLabels(columns_name)
        self.table_data.doubleClicked.connect(self.ubah_data)
        data_list = []
        data = self.cassandra.get_data(keyspace, table, columns_name)
        for i in data:
            temp =[]
            for j in range(len(columns_name)):
                temp.append(i[j])
            data_list.append(temp)

        total = len(data_list)
        self.table_data.setRowCount(total)

        for dat in range(total):
            for x in range(len(columns_name)):
                self.table_data.setItem(dat, x, QTableWidgetItem(str(data_list[dat][x])))

    def tambah_data(self):
        temp_columns_name = [[i.column_name, i.kind] for i in self.cassandra.get_columns_name(self.keyspace_name, self.table_name)]
        columns_name = []
        for col in temp_columns_name:
            if col[1] != "partition_key":
                columns_name.append(col[0])
            elif col[1] == "partition_key":
                columns_name.insert(0, col[0])
        self.tambahEditData.columns = columns_name
        # self.tambahEditData.columns = ['id', 'nama', 'hobi']
        self.tambahEditData.keyspace_name = self.keyspace_name
        self.tambahEditData.table_name = self.table_name
        self.tambahEditData.isTambahData = True
        self.tambahEditData.setWindowTitle("Tambah Data")
        self.tambahEditData.generateInput()
        self.tambahEditData.exec_()

    def tambah_and_edit(self, query, action):
        self.cassandra.execute_query(query)
        self.reset_Qtables(data_table = True)
        self.show_data(self.keyspace_name, self.table_name)
        self.alert.setWindowTitle("Berhasil!")
        self.alert.alert_text.setText(f"Data berhasil di{action}!")
        self.alert.exec_()

    def ubah_data(self, index):
        row = index.row()
        temp_columns_name = [[i.column_name, i.kind] for i in self.cassandra.get_columns_name(self.keyspace_name, self.table_name)]
        columns_name = []
        
        for col in temp_columns_name:
            if col[1] != "partition_key":
                columns_name.append(col[0])
            elif col[1] == "partition_key":
                columns_name.insert(0, col[0])
        self.tambahEditData.columns = columns_name
        banyak_column = len(columns_name)
        self.tambahEditData.keyspace_name = self.keyspace_name
        self.tambahEditData.table_name = self.table_name
        self.tambahEditData.isTambahData = False
        try:
            data = [self.table_data.item(row, i).text() for i in range(banyak_column)]
            self.tambahEditData.data = data
            self.tambahEditData.setWindowTitle("Ubah Data")
            self.tambahEditData.generateInput()
            self.tambahEditData.exec_()
        except:
            pass
        

    def filter_data(self):
        temp_columns_name = [[i.column_name, i.kind] for i in self.cassandra.get_columns_name(self.keyspace_name, self.table_name)]
        columns_name = []
        for col in temp_columns_name:
            if col[1] != "partition_key":
                columns_name.append(col[0])
            elif col[1] == "partition_key":
                columns_name.insert(0, col[0])
        self.filter.columns = columns_name
        self.filter.keyspace_name = self.keyspace_name
        self.filter.table_name = self.table_name
        self.filter.generateCheckBoxAndInput()
        self.filter.exec_()
    
    def hasil_filter(self, query, select_list):
        temp_columns_name = [[i.column_name, i.kind] for i in self.cassandra.get_columns_name(self.keyspace_name, self.table_name)]
        columns_name = []
        for col in temp_columns_name:
            if col[0] in select_list:
                if col[1] != "partition_key":
                    columns_name.append(col[0])
                elif col[1] == "partition_key":
                    columns_name.insert(0, col[0])
        self.table_data.setColumnCount(len(columns_name))
        self.table_data.setHorizontalHeaderLabels(columns_name)
        data_list = []
        data = self.cassandra.execute_query(query)
        self.reset_Qtables(data_table=True)
        for i in data:
            temp =[]
            for j in range(len(columns_name)):
                temp.append(i[j])
            data_list.append(temp)

        total = len(data_list)
        self.table_data.setRowCount(total)

        for dat in range(total):
            for x in range(len(columns_name)):
                self.table_data.setItem(dat, x, QTableWidgetItem(str(data_list[dat][x])))

    def reset_Qtables(self, all = False, keyspace_table = False, table_table = False, data_table = False):
        if all == True:
            self.table_keyspace.setRowCount(0)
            self.table_table.setRowCount(0)
        if keyspace_table == True:
            self.table_keyspace.setRowCount(0)
        if table_table == True:
            self.table_table.setRowCount(0)
        if data_table == True:
            self.table_data.setRowCount(0)

    def tambah_keyspace_closed(self, query):
        # self.cassandra.createKeyspace(query)
        self.cassandra.execute_query(query)
        self.reset_Qtables(all = True)
        self.show_keyspaces()
        self.alert.setWindowTitle("Berhasil!")
        self.alert.alert_text.setText("Keyspace berhasil dibuat!")
        self.alert.exec_()

    def tambah_table_closed(self, query):
        self.cassandra.execute_query(query)
        self.reset_Qtables(table_table=True)
        self.show_tables(self.keyspace_name)
        self.alert.setWindowTitle("Berhasil!")
        self.alert.alert_text.setText("Table berhasil dibuat!")
        self.alert.exec_()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
app.exec_()
import os
import sys
import time
from getmac import get_mac_address
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import QFile, QThread, pyqtSignal, Qt, QPersistentModelIndex

from custom_pySmartDL import SmartDL
from custom_winping import winping
from config_modem import ConfigModem, AC1000F, G97RG_Model
from database import test_result_db, modem_series_db, config_modem_data_db, check_test_data_db, test_data_db
import write_excel_file
import custom_cmd


class MyTableWidgetItem(QTableWidgetItem):
    def __init__(self, str, status=None):
        super(MyTableWidgetItem, self).__init__(str)
        self.setTextAlignment(Qt.AlignCenter)

        if status is True:
            self.setBackground(QColor(0, 0, 127, 255))
        elif status is False:
            self.setBackground(QColor(255, 0, 0, 255))


class InputCheckModem(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi('check_modem.ui', self)

        self.load_check_test_table()

        self.save_check_btn.clicked.connect(self.on_save_check)

    def on_save_check(self):
        data = list()
        for i in [1, 2, 3, 4]:
            for j in [2, 3, 4, 5]:
                try:
                    a = self.check_test_table.item(j, i).text()
                    data.append(a)
                except:
                    data.append('')

        data.append(self.check_test_table.item(6, 1).text())
        data.append(self.check_test_table.item(6, 4).text())
        data.append(self.check_test_table.item(7, 4).text())
        try:
            check_test_data_db.update_check_test_data(data)
            QMessageBox.information(
                self, 'Thông báo', 'Lưu thông tin kiểm tra modem thành công.', QMessageBox.Yes, QMessageBox.Yes)
        except:
            QMessageBox.warning(
                self, 'Thông báo', 'Không lưu được thông tin kiểm tra modem.', QMessageBox.Yes, QMessageBox.Yes)

    def load_check_test_table(self):
        self.check_test_table.setSpan(0, 1, 1, 2)
        self.check_test_table.setSpan(0, 3, 1, 2)
        self.check_test_table.setSpan(6, 0, 2, 1)
        self.check_test_table.setSpan(6, 1, 2, 2)

        self.check_test_table.setItem(0, 1, MyTableWidgetItem('LAN'))
        self.check_test_table.setItem(0, 3, MyTableWidgetItem('WIFI'))

        self.check_test_table.setItem(1, 1, MyTableWidgetItem('Time (ms)'))
        self.check_test_table.setItem(1, 2, MyTableWidgetItem('Loss (%)'))
        self.check_test_table.setItem(1, 3, MyTableWidgetItem('Time (ms)'))
        self.check_test_table.setItem(1, 4, MyTableWidgetItem('Loss (%)'))

        self.check_test_table.setItem(2, 0, QTableWidgetItem('Gateway'))
        self.check_test_table.setItem(3, 0, QTableWidgetItem('DNS FPT'))
        self.check_test_table.setItem(4, 0, QTableWidgetItem('24h.com.vn'))
        self.check_test_table.setItem(5, 0, QTableWidgetItem('DNS Google'))

        self.check_test_table.setItem(6, 0, QTableWidgetItem('Download Speed'))
        self.check_test_table.setItem(6, 3, QTableWidgetItem('Wifi 2.4G:'))
        self.check_test_table.setItem(7, 3, QTableWidgetItem('Wifi 5G:'))

        self.check_test_table.setColumnWidth(0, 100)
        self.check_test_table.setColumnWidth(1, 90)
        self.check_test_table.setColumnWidth(2, 90)
        self.check_test_table.setColumnWidth(3, 90)
        self.check_test_table.setColumnWidth(4, 90)

        index = 1
        data = check_test_data_db.get_check_test_data()
        for i in [1, 2, 3, 4]:
            for j in [2, 3, 4, 5]:
                self.check_test_table.setItem(
                    j, i, MyTableWidgetItem(str(data[index])))
                index += 1

        self.check_test_table.setItem(6, 1, MyTableWidgetItem(str(data[-3])))
        self.check_test_table.setItem(6, 4, MyTableWidgetItem(str(data[-2])))
        self.check_test_table.setItem(7, 4, MyTableWidgetItem(str(data[-1])))

#ok
class InputConfigModem_G97RG3(QWidget):
    def __init__(self, obj):
        QWidget.__init__(self)
        uic.loadUi('config_g97rg3.ui', self)

        self.dev_name = obj.dev_name

        self.load_config_modem()

        self.select_firmware_btn.clicked.connect(self.on_select_firmware)
        self.save_config_btn.clicked.connect(self.on_save_config)

    def on_select_firmware(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn Firmware")
        self.firmware_path.setText(file_name)

    def on_save_config(self):
        try:
            list_data = [
                self.wan_account.text().strip(),
                self.wan_password.text().strip(),
                self.wifi24_mode.currentData(),
                self.wifi24_channel.currentData(),
                self.wifi24_bandwidth.currentData(),
                '', '', '',
                self.firmware_name.text().strip(),
                self.firmware_path.text().strip(),
                self.dev_name.text()
            ]
            config_data = config_modem_data_db.get_config_modem_by_name(
                self.dev_name.text())
            if config_data is None:
                config_modem_data_db.create_new_config_modem_data(
                    self.dev_name.text())
                config_modem_data_db.update_config_modem_data(list_data)
            else:
                config_modem_data_db.update_config_modem_data(list_data)
            QMessageBox.information(
                self, 'Thông báo', 'Lưu thông tin cấu hình modem thành công.', QMessageBox.Yes, QMessageBox.Yes)

        except:
            QMessageBox.warning(
                self, 'Thông báo', 'Không lưu được thông tin cấu hình modem.', QMessageBox.Yes, QMessageBox.Yes)

    def load_config_modem(self):
        list_wifi24_mode = {
            '0': 'Auto(802.11b/g/n)',
            '1': '802.11g/n',
            '3': '802.11n Only',
            '4': '802.11g Only',
            '5': '802.11b Only'
        }
        list_wifi24_channel = {
            '0': 'Auto Selection',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13'
        }
        list_wifi24_bandwidth = {
            '0': '20M',
            '1': '40M'
        }
        try:
            config_modem_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_modem_data is not None:
                self.wan_account.setText(config_modem_data[1])
                self.wan_password.setText(config_modem_data[2])
                self.firmware_name.setText(config_modem_data[9])
                self.firmware_path.setText(config_modem_data[10])

                self.wifi24_mode.clear()

                if config_modem_data[3] != '':
                    self.wifi24_mode.addItem(list_wifi24_mode[config_modem_data[3]], config_modem_data[3])
                    list_wifi24_mode.pop(config_modem_data[3])
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)
                else:
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)

                self.wifi24_channel.clear()
                
                if config_modem_data[4] != '':
                    self.wifi24_channel.addItem(list_wifi24_channel[config_modem_data[4]], config_modem_data[4])
                    list_wifi24_channel.pop(config_modem_data[4])
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
                else:
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
            

                self.wifi24_bandwidth.clear()

                if config_modem_data[5] != '':
                    self.wifi24_bandwidth.addItem(list_wifi24_bandwidth[config_modem_data[5]], config_modem_data[5])
                    list_wifi24_bandwidth.pop(config_modem_data[5])
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)
                else:
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)
        except:
            self.wifi24_mode.clear()
            self.wifi24_channel.clear()
            self.wifi24_bandwidth.clear()

            for key, value in list_wifi24_mode.items():
                self.wifi24_mode.addItem(value, key)
            for key, value in list_wifi24_channel.items():
                self.wifi24_channel.addItem(value, key)
            for key, value in list_wifi24_bandwidth.items():
                self.wifi24_bandwidth.addItem(value, key)

#ok
class InputConfigModem_G97D2(QWidget):
    def __init__(self, obj):
        QWidget.__init__(self)
        uic.loadUi('config_g97d2.ui', self)

        self.dev_name = obj.dev_name

        self.load_config_modem()

        self.select_firmware_btn.clicked.connect(self.on_select_firmware)
        self.save_config_btn.clicked.connect(self.on_save_config)

    def on_select_firmware(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn Firmware")
        self.firmware_path.setText(file_name)

    def on_save_config(self):
        try:
            list_data = [
                self.wan_account.text().strip(),
                self.wan_password.text().strip(),
                self.wifi24_mode.currentData(),
                self.wifi24_channel.currentData(),
                self.wifi24_bandwidth.currentData(),
                '', '', '',
                self.firmware_name.text().strip(),
                self.firmware_path.text().strip(),
                self.dev_name.text()
            ]
            config_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_data is None:
                config_modem_data_db.create_new_config_modem_data(self.dev_name.text())
                config_modem_data_db.update_config_modem_data(list_data)
            else:
                config_modem_data_db.update_config_modem_data(list_data)
            QMessageBox.information(self, 'Thông báo', 'Lưu thông tin cấu hình modem thành công.', QMessageBox.Yes, QMessageBox.Yes)

        except:
            QMessageBox.warning(self, 'Thông báo', 'Không lưu được thông tin cấu hình modem.', QMessageBox.Yes, QMessageBox.Yes)

    def load_config_modem(self):
        list_wifi24_mode = {
            '0': 'Auto(802.11b/g/n)',
            '1': '802.11g/n',
            '3': '802.11n Only',
            '4': '802.11g Only',
            '5': '802.11b Only'
        }
        list_wifi24_channel = {
            '0': 'Auto Selection',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13'
        }
        list_wifi24_bandwidth = {
            '0': '20M',
            '1': '40M'
        }
        try:
            config_modem_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_modem_data is not None:
                self.wan_account.setText(config_modem_data[1])
                self.wan_password.setText(config_modem_data[2])
                self.firmware_name.setText(config_modem_data[9])
                self.firmware_path.setText(config_modem_data[10])

                self.wifi24_mode.clear()

                if config_modem_data[3] != '':
                    self.wifi24_mode.addItem(list_wifi24_mode[config_modem_data[3]], config_modem_data[3])
                    list_wifi24_mode.pop(config_modem_data[3])
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)
                else:
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)

                self.wifi24_channel.clear()
                
                if config_modem_data[4] != '':
                    self.wifi24_channel.addItem(list_wifi24_channel[config_modem_data[4]], config_modem_data[4])
                    list_wifi24_channel.pop(config_modem_data[4])
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
                else:
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
            

                self.wifi24_bandwidth.clear()

                if config_modem_data[5] != '':
                    self.wifi24_bandwidth.addItem(list_wifi24_bandwidth[config_modem_data[5]], config_modem_data[5])
                    list_wifi24_bandwidth.pop(config_modem_data[5])
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)
                else:
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)
        except:
            self.wifi24_mode.clear()
            self.wifi24_channel.clear()
            self.wifi24_bandwidth.clear()

            for key, value in list_wifi24_mode.items():
                self.wifi24_mode.addItem(value, key)
            for key, value in list_wifi24_channel.items():
                self.wifi24_channel.addItem(value, key)
            for key, value in list_wifi24_bandwidth.items():
                self.wifi24_bandwidth.addItem(value, key)

#ok
class InputConfigModem_G97RG6M(QWidget):
    def __init__(self, obj):
        QWidget.__init__(self)
        uic.loadUi('config_g97rg6m.ui', self)

        self.dev_name = obj.dev_name

        self.load_config_modem()

        self.select_firmware_btn.clicked.connect(self.on_select_firmware)
        self.save_config_btn.clicked.connect(self.on_save_config)

    def on_select_firmware(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn Firmware")
        self.firmware_path.setText(file_name)

    def on_save_config(self):
        try:
            list_data = [
                self.wan_account.text().strip(),
                self.wan_password.text().strip(),
                self.wifi24_mode.currentData(),
                self.wifi24_channel.currentData(),
                self.wifi24_bandwidth.currentData(),
                self.wifi5_mode.currentData(),
                self.wifi5_channel.currentData(),
                self.wifi5_bandwidth.currentData(),
                self.firmware_name.text().strip(),
                self.firmware_path.text().strip(),
                self.dev_name.text()
            ]
            config_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_data is None:
                config_modem_data_db.create_new_config_modem_data(self.dev_name.text())
                config_modem_data_db.update_config_modem_data(list_data)
            else:
                config_modem_data_db.update_config_modem_data(list_data)
            QMessageBox.information(self, 'Thông báo', 'Lưu thông tin cấu hình modem thành công.', QMessageBox.Yes, QMessageBox.Yes)

        except:
            QMessageBox.warning(self, 'Thông báo', 'Không lưu được thông tin cấu hình modem.', QMessageBox.Yes, QMessageBox.Yes)

    def load_config_modem(self):
        list_wifi24_mode = {
            '0': 'Auto(802.11b/g/n)',
            '1': '802.11g/n',
            '3': '802.11n Only',
            '4': '802.11g Only',
            '5': '802.11b Only'
        }
        list_wifi24_channel = {
            '0': 'Auto Selection',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13'
        }
        list_wifi24_bandwidth = {
            '0': '20M',
            '1': '40M'
        }
        list_wifi5_mode = {
            '0': 'Auto(802.11 a/n/ac)',
            '6': '802.11a Only',
            '7': '802.11a/n',
            '8': '802.11ac'
        }
        list_wifi5_channel = {
            '0': 'Auto Selection',
            '36': '36',
            '40': '40',
            '44': '44',
            '48': '48',
            '52': '52',
            '56': '56',
            '60': '60',
            '64': '64',
            '149': '149',
            '153': '153',
            '157': '157',
            '161': '161',
            '165': '165'
        }
        try:
            config_modem_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_modem_data is not None:

                self.wan_account.setText(config_modem_data[1])
                self.wan_password.setText(config_modem_data[2])
                self.firmware_name.setText(config_modem_data[9])
                self.firmware_path.setText(config_modem_data[10])

                self.wifi24_mode.clear()
                
                if config_modem_data[3] != '':
                    self.wifi24_mode.addItem(list_wifi24_mode[config_modem_data[3]], config_modem_data[3])
                    list_wifi24_mode.pop(config_modem_data[3])
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)
                else:
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)

                self.wifi24_channel.clear()
                
                if config_modem_data[4] != '':
                    self.wifi24_channel.addItem(list_wifi24_channel[config_modem_data[4]], config_modem_data[4])
                    list_wifi24_channel.pop(config_modem_data[4])
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
                else:
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
            

                self.wifi24_bandwidth.clear()
                
                if config_modem_data[5] != '':
                    self.wifi24_bandwidth.addItem(list_wifi24_bandwidth[config_modem_data[5]], config_modem_data[5])
                    list_wifi24_bandwidth.pop(config_modem_data[5])
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)
                else:
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)

                self.wifi5_mode.clear()
                
                if config_modem_data[6] != '':
                    self.wifi5_mode.addItem(list_wifi5_mode[config_modem_data[6]], config_modem_data[6])
                    list_wifi5_mode.pop(config_modem_data[6])
                    for key, value in list_wifi5_mode.items():
                        self.wifi5_mode.addItem(value, key)
                else:
                    for key, value in list_wifi5_mode.items():
                        self.wifi5_mode.addItem(value, key)

                self.wifi5_channel.clear()
                
                if config_modem_data[7] != '':
                    self.wifi5_channel.addItem(list_wifi5_channel[config_modem_data[7]], config_modem_data[7])
                    list_wifi5_channel.pop(config_modem_data[7])
                    for key, value in list_wifi5_channel.items():
                        self.wifi5_channel.addItem(value, key)
                else:
                    for key, value in list_wifi5_channel.items():
                        self.wifi5_channel.addItem(value, key)

                self.wifi5_bandwidth.clear()
                self.wifi5_bandwidth.addItem('Auto', '3')
        except:
            self.wifi24_mode.clear()
            for key, value in list_wifi24_mode.items():
                self.wifi24_mode.addItem(value, key)

            self.wifi24_channel.clear()
            for key, value in list_wifi24_channel.items():
                self.wifi24_channel.addItem(value, key)

            self.wifi24_bandwidth.clear()
            for key, value in list_wifi24_bandwidth.items():
                self.wifi24_bandwidth.addItem(value, key)

            self.wifi5_mode.clear()
            for key, value in list_wifi5_mode.items():
                self.wifi5_mode.addItem(value, key)

            self.wifi5_channel.clear()
            for key, value in list_wifi5_channel.items():
                self.wifi5_channel.addItem(value, key)

            self.wifi5_bandwidth.clear()
            self.wifi5_bandwidth.addItem('Auto', '3')

#ok
class InputConfigModem_G97RG6W(QWidget):
    def __init__(self, obj):
        QWidget.__init__(self)
        uic.loadUi('config_g97rg6w.ui', self)

        self.dev_name = obj.dev_name

        self.load_config_modem()

        self.select_firmware_btn.clicked.connect(self.on_select_firmware)
        self.save_config_btn.clicked.connect(self.on_save_config)

    def on_select_firmware(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn Firmware")
        self.firmware_path.setText(file_name)

    def on_save_config(self):
        try:
            list_data = [
                self.wan_account.text().strip(),
                self.wan_password.text().strip(),
                self.wifi24_mode.currentData(),
                self.wifi24_channel.currentData(),
                self.wifi24_bandwidth.currentData(),
                self.wifi5_mode.currentData(),
                self.wifi5_channel.currentData(),
                self.wifi5_bandwidth.currentData(),
                self.firmware_name.text().strip(),
                self.firmware_path.text().strip(),
                self.dev_name.text()
            ]
            config_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_data is None:
                config_modem_data_db.create_new_config_modem_data(self.dev_name.text())
                config_modem_data_db.update_config_modem_data(list_data)
            else:
                config_modem_data_db.update_config_modem_data(list_data)
            QMessageBox.information(self, 'Thông báo', 'Lưu thông tin cấu hình modem thành công.', QMessageBox.Yes, QMessageBox.Yes)

        except:
            QMessageBox.warning(self, 'Thông báo', 'Không lưu được thông tin cấu hình modem.', QMessageBox.Yes, QMessageBox.Yes)

    def load_config_modem(self):
        list_wifi24_mode = {
            '0': 'Auto(802.11b/g/n)',
            '1': '802.11g/n',
            '3': '802.11n Only',
            '4': '802.11g Only',
            '5': '802.11b Only'
        }
        list_wifi24_channel = {
            '0': 'Auto Selection',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13'
        }
        list_wifi24_bandwidth = {
            '0': '20M',
            '1': '40M'
        }
        list_wifi5_mode = {
            '0': 'Auto(802.11 a/n/ac)',
            '6': '802.11a Only',
            '7': '802.11a/n',
            '8': '802.11ac'
        }
        list_wifi5_channel = {
            '0': 'Auto Selection',
            '36': '36',
            '40': '40',
            '44': '44',
            '48': '48',
            '52': '52',
            '56': '56',
            '60': '60',
            '64': '64',
            '149': '149',
            '153': '153',
            '157': '157',
            '161': '161',
            '165': '165'
        }
        try:
            config_modem_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_modem_data is not None:

                self.wan_account.setText(config_modem_data[1])
                self.wan_password.setText(config_modem_data[2])
                self.firmware_name.setText(config_modem_data[9])
                self.firmware_path.setText(config_modem_data[10])

                self.wifi24_mode.clear()
                
                if config_modem_data[3] != '':
                    self.wifi24_mode.addItem(list_wifi24_mode[config_modem_data[3]], config_modem_data[3])
                    list_wifi24_mode.pop(config_modem_data[3])
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)
                else:
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)

                self.wifi24_channel.clear()
                
                if config_modem_data[4] != '':
                    self.wifi24_channel.addItem(list_wifi24_channel[config_modem_data[4]], config_modem_data[4])
                    list_wifi24_channel.pop(config_modem_data[4])
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
                else:
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
            

                self.wifi24_bandwidth.clear()
                
                if config_modem_data[5] != '':
                    self.wifi24_bandwidth.addItem(list_wifi24_bandwidth[config_modem_data[5]], config_modem_data[5])
                    list_wifi24_bandwidth.pop(config_modem_data[5])
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)
                else:
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)

                self.wifi5_mode.clear()
                
                if config_modem_data[6] != '':
                    self.wifi5_mode.addItem(list_wifi5_mode[config_modem_data[6]], config_modem_data[6])
                    list_wifi5_mode.pop(config_modem_data[6])
                    for key, value in list_wifi5_mode.items():
                        self.wifi5_mode.addItem(value, key)
                else:
                    for key, value in list_wifi5_mode.items():
                        self.wifi5_mode.addItem(value, key)

                self.wifi5_channel.clear()
                
                if config_modem_data[7] != '':
                    self.wifi5_channel.addItem(list_wifi5_channel[config_modem_data[7]], config_modem_data[7])
                    list_wifi5_channel.pop(config_modem_data[7])
                    for key, value in list_wifi5_channel.items():
                        self.wifi5_channel.addItem(value, key)
                else:
                    for key, value in list_wifi5_channel.items():
                        self.wifi5_channel.addItem(value, key)

                self.wifi5_bandwidth.clear()
                self.wifi5_bandwidth.addItem('Auto', '3')
        except:
            self.wifi24_mode.clear()
            for key, value in list_wifi24_mode.items():
                self.wifi24_mode.addItem(value, key)

            self.wifi24_channel.clear()
            for key, value in list_wifi24_channel.items():
                self.wifi24_channel.addItem(value, key)

            self.wifi24_bandwidth.clear()
            for key, value in list_wifi24_bandwidth.items():
                self.wifi24_bandwidth.addItem(value, key)

            self.wifi5_mode.clear()
            for key, value in list_wifi5_mode.items():
                self.wifi5_mode.addItem(value, key)

            self.wifi5_channel.clear()
            for key, value in list_wifi5_channel.items():
                self.wifi5_channel.addItem(value, key)

            self.wifi5_bandwidth.clear()
            self.wifi5_bandwidth.addItem('Auto', '3')

#ok
class InputConfigModem_C30401(QWidget):
    def __init__(self, obj):
        QWidget.__init__(self)
        uic.loadUi('config_c30401.ui', self)

        self.dev_name = obj.dev_name

        self.load_config_modem()

        self.select_firmware_btn.clicked.connect(self.on_select_firmware)
        self.save_config_btn.clicked.connect(self.on_save_config)

    def on_select_firmware(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn Firmware")
        self.firmware_path.setText(file_name)

    def on_save_config(self):
        try:
            list_data = [
                self.wan_account.text().strip(),
                self.wan_password.text().strip(),
                self.wifi24_mode.currentData(),
                self.wifi24_channel.currentData(),
                self.wifi24_bandwidth.currentData(),
                self.wifi5_mode.currentData(),
                self.wifi5_channel.currentData(),
                self.wifi5_bandwidth.currentData(),
                self.firmware_name.text().strip(),
                self.firmware_path.text().strip(),
                self.dev_name.text()
            ]
            config_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_data is None:
                config_modem_data_db.create_new_config_modem_data(self.dev_name.text())
                config_modem_data_db.update_config_modem_data(list_data)
            else:
                config_modem_data_db.update_config_modem_data(list_data)
            QMessageBox.information(self, 'Thông báo', 'Lưu thông tin cấu hình modem thành công.', QMessageBox.Yes, QMessageBox.Yes)

        except:
            QMessageBox.warning(self, 'Thông báo', 'Không lưu được thông tin cấu hình modem.', QMessageBox.Yes, QMessageBox.Yes)

    def load_config_modem(self):
        list_wifi24_mode = {
            '0': 'Auto(802.11b/g/n)',
            '1': '802.11g/n',
            '3': '802.11n Only',
            '4': '802.11g Only',
            '5': '802.11b Only'
        }
        list_wifi24_channel = {
            '0': 'Auto Selection',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13'
        }
        list_wifi24_bandwidth = {
            '0': '20M',
            '1': '40M'
        }
        list_wifi5_mode = {
            '0': 'Auto(802.11 a/n/ac)',
            '6': '802.11a Only',
            '7': '802.11a/n',
            '8': '802.11ac'
        }
        list_wifi5_channel = {
            '0': 'Auto Selection',
            '36': '36',
            '40': '40',
            '44': '44',
            '48': '48',
            '52': '52',
            '56': '56',
            '60': '60',
            '64': '64',
            '149': '149',
            '153': '153',
            '157': '157',
            '161': '161',
            '165': '165'
        }
        try:
            config_modem_data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if config_modem_data is not None:

                self.wan_account.setText(config_modem_data[1])
                self.wan_password.setText(config_modem_data[2])
                self.firmware_name.setText(config_modem_data[9])
                self.firmware_path.setText(config_modem_data[10])

                self.wifi24_mode.clear()
                
                if config_modem_data[3] != '':
                    self.wifi24_mode.addItem(list_wifi24_mode[config_modem_data[3]], config_modem_data[3])
                    list_wifi24_mode.pop(config_modem_data[3])
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)
                else:
                    for key, value in list_wifi24_mode.items():
                        self.wifi24_mode.addItem(value, key)

                self.wifi24_channel.clear()
                
                if config_modem_data[4] != '':
                    self.wifi24_channel.addItem(list_wifi24_channel[config_modem_data[4]], config_modem_data[4])
                    list_wifi24_channel.pop(config_modem_data[4])
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
                else:
                    for key, value in list_wifi24_channel.items():
                        self.wifi24_channel.addItem(value, key)
            

                self.wifi24_bandwidth.clear()
                
                if config_modem_data[5] != '':
                    self.wifi24_bandwidth.addItem(list_wifi24_bandwidth[config_modem_data[5]], config_modem_data[5])
                    list_wifi24_bandwidth.pop(config_modem_data[5])
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)
                else:
                    for key, value in list_wifi24_bandwidth.items():
                        self.wifi24_bandwidth.addItem(value, key)

                self.wifi5_mode.clear()
                
                if config_modem_data[6] != '':
                    self.wifi5_mode.addItem(list_wifi5_mode[config_modem_data[6]], config_modem_data[6])
                    list_wifi5_mode.pop(config_modem_data[6])
                    for key, value in list_wifi5_mode.items():
                        self.wifi5_mode.addItem(value, key)
                else:
                    for key, value in list_wifi5_mode.items():
                        self.wifi5_mode.addItem(value, key)

                self.wifi5_channel.clear()
                
                if config_modem_data[7] != '':
                    self.wifi5_channel.addItem(list_wifi5_channel[config_modem_data[7]], config_modem_data[7])
                    list_wifi5_channel.pop(config_modem_data[7])
                    for key, value in list_wifi5_channel.items():
                        self.wifi5_channel.addItem(value, key)
                else:
                    for key, value in list_wifi5_channel.items():
                        self.wifi5_channel.addItem(value, key)

                self.wifi5_bandwidth.clear()
                self.wifi5_bandwidth.addItem('Auto', '3')
        except:
            self.wifi24_mode.clear()
            for key, value in list_wifi24_mode.items():
                self.wifi24_mode.addItem(value, key)

            self.wifi24_channel.clear()
            for key, value in list_wifi24_channel.items():
                self.wifi24_channel.addItem(value, key)

            self.wifi24_bandwidth.clear()
            for key, value in list_wifi24_bandwidth.items():
                self.wifi24_bandwidth.addItem(value, key)

            self.wifi5_mode.clear()
            for key, value in list_wifi5_mode.items():
                self.wifi5_mode.addItem(value, key)

            self.wifi5_channel.clear()
            for key, value in list_wifi5_channel.items():
                self.wifi5_channel.addItem(value, key)

            self.wifi5_bandwidth.clear()
            self.wifi5_bandwidth.addItem('Auto', '3')


class ThreadTestAll(QThread):
    console_test_modem_sig = pyqtSignal(str)
    progress_bar_sig = pyqtSignal(dict)
    test_result_sig = pyqtSignal(dict)
    download_progress_sig = pyqtSignal(dict)
    finish_flag_sig = pyqtSignal(str)
    error_sig = pyqtSignal(str)

    def __init__(self, obj, parent=None):
        self.obj = obj
        self.approximate = 0.98
        QThread.__init__(self, parent=parent)

    def on_source(self, data):
        self.dev_name = data['dev_name']
        self.dev_macwan = data['dev_macwan']
        self.dev_firmware = data['dev_fw']
        self.dev_username = data['dev_username']
        self.dev_password = data['dev_password']
        self.conf = data['conf']

    def upgrade_firmware(self):
        if self.firmware_name == '':
            self.console_test_modem_sig.emit('Không tìm thấy firmware, xin kiểm tra lại.')
        else:
            if self.dev_name == 'G-97RG3' or self.dev_name == 'G-97D2' or self.dev_name == 'G-97RG6M' or self.dev_name == 'C30-401':
                self.console_test_modem_sig.emit('Upgrade Firmware ...')
                g97rg_model = G97RG_Model(self.dev_username, self.dev_password)
                login = g97rg_model.login_modem()
                self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
                if login == 200:
                    check = g97rg_model.update_firmware(self.firmware_path)
                    if check == 200:
                        for i in range(101):
                            self.progress_bar_sig.emit({
                                'value': i
                            })
                            self.sleep(1)
                        self.console_test_modem_sig.emit('Upgrade Firmware thành công. Đang đợi kết nối lại....')
                        self.sleep(150)
                    else:
                        self.console_test_modem_sig.emit('Upgrade Firmware thất bại.')
            elif self.dev_name == 'AC1000F':
                ac1000f = AC1000F(self.dev_username, self.dev_password)
                login = ac1000f.login()
                self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
                if login == 200:
                    check = ac1000f.update_firmware(self.firmware_path)
                    if check == 200:
                        for i in range(101):
                            self.progress_bar_sig.emit({
                                'value': i
                            })
                            self.sleep(1)
                        self.console_test_modem_sig.emit('Upgrade Firmware thành công. Đang đợi kết nối lại....')
                        self.sleep(150)
                    else:
                        self.console_test_modem_sig.emit('Upgrade Firmware thất bại.')

    def config_modem(self):
        self.console_test_modem_sig.emit('Cấu hình modem ' + self.dev_name + ':')
        if self.dev_name == 'G-97RG3' or self.dev_name == 'G-97D2':
            g97rg3 = G97RG_Model(
                self.dev_username, 
                self.dev_password, 
                self.wan_account, 
                self.wan_password,
                self.wifi24_ssid, 
                self.wifi24_pass, 
                self.wifi24_mode, 
                self.wifi24_channel, 
                self.wifi24_bandwidth
            )
            login = g97rg3.login_modem()
            self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
            self.sleep(1)
            
            if login == 200:
                self.console_test_modem_sig.emit('Config Wifi 2.4G:')
                check = g97rg3.config_wifi_24g_basic()
                self.console_test_modem_sig.emit('    Basic: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg3.config_wifi_24g_ssid()
                self.console_test_modem_sig.emit('    SSID: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg3.config_wifi_24g_secutity()
                self.console_test_modem_sig.emit('    Security: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg3.config_wan()
                self.console_test_modem_sig.emit('Config WAN: <<%d>>' % (check))
                self.sleep(1)
            self.console_test_modem_sig.emit('========================')

        elif self.dev_name == 'G-97RG6M' or self.dev_name == 'C30-401' or self.dev_name == 'G-97RG6W':
            g97rg6m = G97RG_Model(
                self.dev_username, self.dev_password, 
                self.wan_account, self.wan_password,
                self.wifi24_ssid, self.wifi24_pass, 
                self.wifi24_mode, self.wifi24_channel, self.wifi24_bandwidth,
                self.wifi5_ssid , self.wifi5_pass , 
                self.wifi5_mode , self.wifi5_channel , self.wifi5_bandwidth)
            login = g97rg6m.login_modem()
            self.console_test_modem_sig.emit('Login: <<%d>>' % (login))     
            self.sleep(1)
            if login == 200:
                self.console_test_modem_sig.emit('Config Wifi 2.4G:')    
                check = g97rg6m.config_wifi_24g_basic()
                self.console_test_modem_sig.emit('    Basic: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg6m.config_wifi_24g_ssid()
                self.console_test_modem_sig.emit('    SSID: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg6m.config_wifi_24g_secutity()
                self.console_test_modem_sig.emit('    Security: <<%d>>' % (check))
                self.sleep(1)

                self.console_test_modem_sig.emit('Config Wifi 5G:')
                check = g97rg6m.config_wifi_5g_basic()
                self.console_test_modem_sig.emit('    Basic: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg6m.config_wifi_5g_ssid()
                self.console_test_modem_sig.emit('    SSID: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg6m.config_wifi_5g_secutity()
                self.console_test_modem_sig.emit('    Security: <<%d>>' % (check))
                self.sleep(1)
                check = g97rg6m.config_wan()
                self.console_test_modem_sig.emit('Config WAN: <<%d>>' % (check))
                self.sleep(1)
            self.console_test_modem_sig.emit('========================')

        elif self.dev_name == 'AC1000F':
            ac1000f = AC1000F(self.dev_username, self.dev_password, self.wan_account, self.wan_password,
                self.wifi24_ssid, self.wifi_24_pass, self.wifi_24_mode, self.wifi_24_channel, self.wifi_24_bandwidth,
                self.wifi_5_ssid, self.wifi_5_pass, self.wifi_5_mode, self.wifi_5_channel, self.wifi_5_bandwidth)

            login = ac1000f.login()
            self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
            self.sleep(1)
            if login == 200:
                check = ac1000f.config_wifi_24g()
                self.console_test_modem_sig.emit('Config Wifi 2.4G: <<%d>>' % (check))
                self.sleep(1)

                check = ac1000f.config_wifi_5g()
                self.console_test_modem_sig.emit('Config Wifi 5G: <<%d>>' % (check))
                self.sleep(1)

                check = ac1000f.config_wan()
                self.console_test_modem_sig.emit('Config WAN: <<%d>>' % (check))
                self.sleep(1)

                check = ac1000f.logout()
                self.console_test_modem_sig.emit('========================')

    def test_lan(self):
        for index in [1, 2, 3]:
            self.console_test_modem_sig.emit('Kiểm tra lần %s:' % (str(index)))
            list_check_ping = list()
            for i in range(4):
                host = self.list_host[i].strip().split()
                try:
                    check_ping_time = float(self.check_lan[i]['time'])
                except:
                    check_ping_time = 0.0

                try:
                    check_ping_loss = float(self.check_lan[i]['loss'])
                except:
                    check_ping_loss = 0.0

                address = host[3]
                count = int(host[2])
                try:
                    a = winping(address=address, count=count)
                    self.console_test_modem_sig.emit(a['data'])
                    try:
                        ping_time = float(a['time'])
                    except:
                        ping_time = 999

                    try:
                        ping_loss = float(a['loss'])
                    except:
                        ping_loss = 100
                    
                    if ping_time <= check_ping_time and ping_loss <= check_ping_loss:
                        list_check_ping.append('OK')
                    else:
                        list_check_ping.append('NOK')
                except:
                    self.console_test_modem_sig.emit('Xảy ra lỗi khi ping ' + address)
                    list_check_ping.append('Không ping được ip ' + address)
                    self.error_sig.emit('Không ping được ip ' + address)

            test_ping = 'OK'
            for check in list_check_ping:
                if check != 'OK':
                    test_ping = 'NOK'
                    break

            # test download:
            try:
                self.smart_download = SmartDL(
                    urls=self.lan_download_url,
                    max_speed=self.lan_speed,
                    progress_sig=self.download_progress_sig,
                    dest=os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
                )
                self.smart_download.start()
                download_speed = self.smart_download.get_speed_download()
                
                on_dinh = 'OK'
                ket_luan = 'OK'
                length = len(download_speed)
                step = 30
                count_error = 1 if round(length * 0.3 / step) == 0 else round(length * 0.3 / step)
                for i in range(0, length, step):
                    a = download_speed[i: i + step]
                    avg = sum(a) / len(a)
                    avg = round(avg / 1000000 * 8, 2)
                    if avg < self.lan_speed * (self.approximate - 0.03):
                        count_error = count_error - 1
                    if count_error <= 0:
                        on_dinh = 'NOK'
                        ket_luan = 'NOK'
                        break

                avg_speed = sum(download_speed) / len(download_speed)
                avg_speed = round(avg_speed / 1000000 * 8, 2)
            except Exception as e:
                avg_speed = 0.0
                on_dinh = 'NOK'
                ket_luan = 'NOK'
                self.error_sig.emit('Xảy ra lỗi khi download.')

            
            if test_ping != 'OK' or avg_speed < self.lan_speed:
                ket_luan = 'NOK'

            self.test_result_sig.emit({
                'index': index,
                'conn': 'lan',
                'ping_time': test_ping,
                'down_rate': avg_speed,
                'on_dinh': on_dinh,
                'ket_luan': ket_luan
            })
            self.sleep(5)
            
    def test_wifi(self):
        for index in [1, 2, 3]:
            self.console_test_modem_sig.emit('Kiểm tra lần %s:' % (str(index)))
            list_check_ping = list()
            for i in range(4):
                host = self.list_host[i].strip().split()
                try:
                    check_ping_time = float(self.check_wifi[i]['time'])
                except:
                    check_ping_time = 0.0

                try:
                    check_ping_loss = float(self.check_wifi[i]['loss'])
                except:
                    check_ping_loss = 0.0

                address = host[3]
                count = int(host[2])
                try:
                    a = winping(address=address, count=count)
                    self.console_test_modem_sig.emit(a['data'])
                    try:
                        ping_time = float(a['time'])
                    except:
                        ping_time = 999

                    try:
                        ping_loss = float(a['loss'])
                    except:
                        ping_loss = 100
                    
                    if ping_time <= check_ping_time and ping_loss <= check_ping_loss:
                        list_check_ping.append('OK')
                    else:
                        list_check_ping.append('NOK')
                except:
                    self.console_test_modem_sig.emit('Xảy ra lỗi khi ping ' + address)
                    list_check_ping.append('Không ping được ip ' + address)
                    self.error_sig.emit('Không ping được ip ' + address)

            test_ping = 'OK'
            for check in list_check_ping:
                if check != 'OK':
                    test_ping = 'NOK'
                    break

            # test download:
            try:
                self.smart_download = SmartDL(
                    urls=self.wifi24_download_url,
                    max_speed=self.wifi24_speed,
                    progress_sig=self.download_progress_sig,
                    dest=os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
                )
                self.smart_download.start()
                download_speed = self.smart_download.get_speed_download()
                
                on_dinh = 'OK'
                ket_luan = 'OK'
                length = len(download_speed)
                step = 30
                count_error = 1 if round(length * 0.3 / step) == 0 else round(length * 0.3 / step)
                for i in range(0, length, step):
                    a = download_speed[i: i + step]
                    avg = sum(a) / len(a)
                    avg = round(avg / 1000000 * 8, 2)
                    if avg < self.wifi24_speed * (self.approximate - 0.03):
                        count_error = count_error - 1
                    if count_error <= 0:
                        on_dinh = 'NOK'
                        ket_luan = 'NOK'
                        break

                avg_speed = sum(download_speed) / len(download_speed)
                avg_speed = round(avg_speed / 1000000 * 8, 2)
            except Exception as e:
                avg_speed = 0.0
                on_dinh = 'NOK'
                ket_luan = 'NOK'
                self.error_sig.emit('Xảy ra lỗi khi download.')
            
            if test_ping != 'OK' or avg_speed < self.wifi24_speed:
                ket_luan = 'NOK'

            self.test_result_sig.emit({
                'index': index,
                'conn': 'wifi',
                'ping_time': test_ping,
                'down_rate': avg_speed,
                'on_dinh': on_dinh,
                'ket_noi_lai': 'OK',
                'ket_luan': ket_luan
            })
            self.sleep(5)

    def test_wifi5(self):
        for index in [1, 2, 3]:
            self.console_test_modem_sig.emit('Kiểm tra lần %s:' % (str(index)))
            list_check_ping = list()
            for i in range(4):
                host = self.list_host[i].strip().split()
                try:
                    check_ping_time = float(self.check_wifi[i]['time'])
                except:
                    check_ping_time = 0.0

                try:
                    check_ping_loss = float(self.check_wifi[i]['loss'])
                except:
                    check_ping_loss = 0.0

                address = host[3]
                count = int(host[2])
                try:
                    a = winping(address=address, count=count)
                    self.console_test_modem_sig.emit(a['data'])
                    try:
                        ping_time = float(a['time'])
                    except:
                        ping_time = 999

                    try:
                        ping_loss = float(a['loss'])
                    except:
                        ping_loss = 100
                    
                    if ping_time <= check_ping_time and ping_loss <= check_ping_loss:
                        list_check_ping.append('OK')
                    else:
                        list_check_ping.append('NOK')
                except:
                    self.console_test_modem_sig.emit('Xảy ra lỗi khi ping ' + address)
                    list_check_ping.append('Không ping được ip ' + address)
                    self.error_sig.emit('Không ping được ip ' + address)

            test_ping = 'OK'
            for check in list_check_ping:
                if check != 'OK':
                    test_ping = 'NOK'
                    break

            # test download:
            try:
                self.smart_download = SmartDL(
                    urls=self.wifi5_download_url,
                    max_speed=self.wifi5_speed,
                    progress_sig=self.download_progress_sig,
                    dest=os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
                )
                self.smart_download.start()
                download_speed = self.smart_download.get_speed_download()

                on_dinh = 'OK'
                ket_luan = 'OK'
                length = len(download_speed)
                step = 30
                count_error = 1 if round(length * 0.3 / step) == 0 else round(length * 0.3 / step)
                for i in range(0, length, step):
                    a = download_speed[i: i + step]
                    avg = sum(a) / len(a)
                    avg = round(avg / 1000000 * 8, 2)
                    if avg < self.wifi5_speed * (self.approximate - 0.03):
                        count_error = count_error - 1
                    if count_error <= 0:
                        on_dinh = 'NOK'
                        ket_luan = 'NOK'
                        break

                avg_speed = sum(download_speed) / len(download_speed)
                avg_speed = round(avg_speed / 1000000 * 8, 2)
            except Exception as e:
                avg_speed = 0.0
                on_dinh = 'NOK'
                ket_luan = 'NOK'
                self.error_sig.emit('Xảy ra lỗi khi download.')

            if test_ping != 'OK' or avg_speed < self.wifi5_speed:
                ket_luan = 'NOK'

            self.test_result_sig.emit({
                'index': index,
                'conn': 'wifi5',
                'ping_time': test_ping,
                'down_rate': avg_speed,
                'on_dinh': on_dinh,
                'ket_noi_lai': 'OK',
                'ket_luan': ket_luan
            })
            self.sleep(5)

    def stop(self):
        try:
            self.smart_download.stop()
        except:
            pass
        
        self.terminate()

    def test_modem(self):
        # custom_cmd.set_metric_interface(
        #     interface='Wi-Fi 2',
        #     metric='1'
        # )

        # custom_cmd.set_metric_interface(
        #     interface='Ethernet',
        #     metric='5'
        # )

        if self.dev_name == 'G-97RG3' or self.dev_name == 'G-97D2':
            try:
                self.console_test_modem_sig.emit('Kiểm tra LAN')
                custom_cmd.disconnect_wlan()
                
                mac_lan = get_mac_address(ip='192.168.1.1')
                if mac_lan is not None:
                    self.test_lan()
                else:
                    raise Exception

            except:
                self.error_sig.emit('Không kết nối được LAN')

            try:
                self.console_test_modem_sig.emit('Kiểm tra WIFI 2.4G')
                custom_cmd.connect_wlan(
                    _ssid=self.wifi24_ssid,
                    _pass=self.wifi24_pass
                )
                self.test_wifi()
            except:
                self.error_sig.emit('Không kết nối được WIFI 2.4G')
                
        elif self.dev_name == 'G-97RG6M' or self.dev_name == 'C30-401' or self.dev_name == 'AC1000F' or self.dev_name == 'G-97RG6W':
            try:
                self.console_test_modem_sig.emit('Kiểm tra LAN')
                custom_cmd.disconnect_wlan()
                
                mac_lan = get_mac_address(ip='192.168.1.1')
                if mac_lan is not None:
                    self.test_lan()
                else:
                    raise Exception

            except:
                self.error_sig.emit('Không kết nối được LAN')

            try:
                self.console_test_modem_sig.emit('Kiểm tra WIFI 2.4G')
                custom_cmd.connect_wlan(
                    _ssid=self.wifi24_ssid,
                    _pass=self.wifi24_pass
                )
                self.test_wifi()
            except:
                self.error_sig.emit('Không kết nối được WIFI 2.4G')

            try:
                self.console_test_modem_sig.emit('Kiểm tra WIFI 5G')
                custom_cmd.connect_wlan(
                    _ssid=self.wifi5_ssid,
                    _pass=self.wifi5_pass
                )
                self.test_wifi5()
            except:
                self.error_sig.emit('Không kết nối được WIFI 5G')
        else:
            pass

    def run(self):
        self.obj.test_modem_btn.setEnabled(False)
        self.obj.update_data_btn.setEnabled(False)
        self.obj.config_modem_btn.setEnabled(False)

        config_modem_data = config_modem_data_db.get_config_modem_by_name(self.dev_name)
        if config_modem_data is not None:
            self.wan_account = config_modem_data[1]
            self.wan_password = config_modem_data[2]
            self.wifi24_ssid = 'FPT Telecom-%s-2.4G' % (self.dev_macwan[8:])
            self.wifi24_pass = '12345678'
            self.wifi24_mode = config_modem_data[3]
            self.wifi24_channel = config_modem_data[4]
            self.wifi24_bandwidth = config_modem_data[5]

            self.wifi5_ssid = 'FPT Telecom-%s-5G' % (self.dev_macwan[8:])
            self.wifi5_pass = '12345678'
            self.wifi5_mode = config_modem_data[6]
            self.wifi5_channel = config_modem_data[7]
            self.wifi5_bandwidth = config_modem_data[8]

            self.firmware_name = config_modem_data[9]
            self.firmware_path = config_modem_data[10]

            # kiểm tra và upgrade firmware
            if self.conf is True:
                if self.dev_firmware == self.firmware_name:
                    pass
                else:
                    self.upgrade_firmware()

                # lấy thông tin thiết bị
                self.obj.on_get_device_info()

                # Cấu hình modem
                self.config_modem()

                self.sleep(30)

            test_data = test_data_db.get_test_data()
            if test_data is not None:
                self.list_host = list(test_data[1:5])
                self.lan_download_url = test_data[-3]
                self.wifi24_download_url = test_data[-2]
                self.wifi5_download_url = test_data[-1]

                check_test_data = check_test_data_db.get_check_test_data()
                if check_test_data is not None:
                    self.check_lan = list()
                    for i in [1, 2, 3, 4]:
                        try:
                            _time = float(check_test_data[i])
                        except:
                            _time = 999
                        
                        try: 
                            _loss = float(check_test_data[i + 4])
                        except:
                            _loss = 999

                        self.check_lan.append({
                            'time': _time,
                            'loss': _loss
                        })

                    self.check_wifi = list()
                    for i in [9, 10, 11, 12]:
                        try:
                            _time = float(check_test_data[i])
                        except:
                            _time = 999
                        
                        try: 
                            _loss = float(check_test_data[i + 4])
                        except:
                            _loss = 999

                        self.check_wifi.append({
                            'time': _time,
                            'loss': _loss
                        })
                    
                    try:
                        self.lan_speed = float(check_test_data[-3])
                    except:
                        self.lan_speed = 999

                    try:
                        self.wifi24_speed = float(check_test_data[-2])
                    except:
                        self.wifi24_speed = 999
                    
                    try:
                        self.wifi5_speed = float(check_test_data[-1])
                    except:
                        self.wifi5_speed = 999

                    self.test_modem()

                    self.finish_flag_sig.emit('Quá trình test hoàn tất.')
                    self.console_test_modem_sig.emit('Quá trình test hoàn tất.')
                    self.obj.test_modem_btn.setEnabled(True)
                    self.obj.update_data_btn.setEnabled(True)
                    self.obj.config_modem_btn.setEnabled(True)
                        
                else:
                    self.error_sig.emit('Không tìm thấy thông tin kiểm tra modem, xin kiểm tra lại.')
                    self.obj.test_modem_btn.setEnabled(True)
                    self.obj.update_data_btn.setEnabled(True)
                    self.obj.config_modem_btn.setEnabled(True)
            else:
                self.error_sig.emit('Không tìm thấy thông tin kiểm tra modem, xin kiểm tra lại.')
                self.obj.test_modem_btn.setEnabled(True)
                self.obj.update_data_btn.setEnabled(True)
                self.obj.config_modem_btn.setEnabled(True)

        else:
            self.error_sig.emit('Không tìm thấy thông tin cấu hình modem, xin kiểm tra lại.')
            self.obj.test_modem_btn.setEnabled(True)
            self.obj.update_data_btn.setEnabled(True)
            self.obj.config_modem_btn.setEnabled(True)


class ThreadConfigModem(QThread):
    console_test_modem_sig = pyqtSignal(str)
    progress_bar_sig = pyqtSignal(dict)
    finish_flag_sig = pyqtSignal(str)
    error_sig = pyqtSignal(str)

    def __init__(self, obj, parent=None):
        self.obj = obj
        QThread.__init__(self, parent=parent)

    def on_source(self, data):
        self.dev_name = data['dev_name']
        self.dev_macwan = data['dev_macwan']
        self.dev_firmware = data['dev_fw']
        self.dev_username = data['dev_username']
        self.dev_password = data['dev_password']

    def upgrade_firmware(self):
        if self.firmware_name == '':
            self.console_test_modem_sig.emit('Không tìm thấy firmware, xin kiểm tra lại.')
        else:
            if self.dev_name == 'G-97RG3' or self.dev_name == 'G-97D2' or self.dev_name == 'G-97RG6M' or self.dev_name == 'C30-401':
                self.console_test_modem_sig.emit('Upgrade Firmware ...')
                g97rg_model = G97RG_Model(self.dev_username, self.dev_password)
                login = g97rg_model.login_modem()
                self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
                if login == 200:
                    check = g97rg_model.update_firmware(self.firmware_path)
                    if check == 200:
                        for i in range(101):
                            self.progress_bar_sig.emit({
                                'value': i
                            })
                            self.sleep(1)
                        self.console_test_modem_sig.emit('Upgrade Firmware thành công. Đang đợi kết nối lại....')
                        self.sleep(150)
                    else:
                        self.console_test_modem_sig.emit('Upgrade Firmware thất bại.')
            elif self.dev_name == 'AC1000F':
                ac1000f = AC1000F(self.dev_username, self.dev_password)
                login = ac1000f.login()
                self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
                if login == 200:
                    check = ac1000f.update_firmware(self.firmware_path)
                    if check == 200:
                        for i in range(101):
                            self.progress_bar_sig.emit({
                                'value': i
                            })
                            self.sleep(1)
                        self.console_test_modem_sig.emit('Upgrade Firmware thành công. Đang đợi kết nối lại....')
                        self.sleep(150)
                    else:
                        self.console_test_modem_sig.emit('Upgrade Firmware thất bại.')

    def config_modem(self):
        self.console_test_modem_sig.emit('Cấu hình modem ' + self.dev_name + ':')
        if self.dev_name == 'G-97RG3' or self.dev_name == 'G-97D2':
            g97rg3 = G97RG_Model(
                self.dev_username, 
                self.dev_password, 
                self.wan_account, 
                self.wan_password,
                self.wifi24_ssid, 
                self.wifi24_pass, 
                self.wifi24_mode, 
                self.wifi24_channel, 
                self.wifi24_bandwidth
            )
            login = g97rg3.login_modem()
            self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
            self.sleep(1)
            if login == 200:
                self.console_test_modem_sig.emit('Config Wifi 2.4G:')
                check = g97rg3.config_wifi_24g_basic()
                self.console_test_modem_sig.emit('    Basic: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg3.config_wifi_24g_ssid()
                self.console_test_modem_sig.emit('    SSID: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg3.config_wifi_24g_secutity()
                self.console_test_modem_sig.emit('    Security: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg3.config_wan()
                self.console_test_modem_sig.emit('Config WAN: <<%d>>' % (check))
                self.sleep(1)
            self.console_test_modem_sig.emit('========================')

        elif self.dev_name == 'G-97RG6M' or self.dev_name == 'C30-401' or self.dev_name == 'G-97RG6W':
            g97rg6m = G97RG_Model(
                self.dev_username, self.dev_password, 
                self.wan_account, self.wan_password,
                self.wifi24_ssid, self.wifi24_pass, 
                self.wifi24_mode, self.wifi24_channel, self.wifi24_bandwidth,
                self.wifi5_ssid , self.wifi5_pass , 
                self.wifi5_mode , self.wifi5_channel , self.wifi5_bandwidth)
            login = g97rg6m.login_modem()
            self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
            self.sleep(1)     

            if login == 200:
                self.console_test_modem_sig.emit('Config Wifi 2.4G:')    
                check = g97rg6m.config_wifi_24g_basic()
                self.console_test_modem_sig.emit('    Basic: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg6m.config_wifi_24g_ssid()
                self.console_test_modem_sig.emit('    SSID: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg6m.config_wifi_24g_secutity()
                self.console_test_modem_sig.emit('    Security: <<%d>>' % (check))
                self.sleep(1)

                self.console_test_modem_sig.emit('Config Wifi 5G:')
                check = g97rg6m.config_wifi_5g_basic()
                self.console_test_modem_sig.emit('    Basic: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg6m.config_wifi_5g_ssid()
                self.console_test_modem_sig.emit('    SSID: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg6m.config_wifi_5g_secutity()
                self.console_test_modem_sig.emit('    Security: <<%d>>' % (check))
                self.sleep(1)

                check = g97rg6m.config_wan()
                self.console_test_modem_sig.emit('Config WAN: <<%d>>' % (check))
                self.sleep(1)
            self.console_test_modem_sig.emit('========================')

        elif self.dev_name == 'AC1000F':
            ac1000f = AC1000F(self.dev_username, self.dev_password, self.wan_account, self.wan_password,
                self.wifi_24_ssid, self.wifi_24_pass, self.wifi_24_mode, self.wifi_24_channel, self.wifi_24_bandwidth,
                self.wifi_5_ssid, self.wifi_5_pass, self.wifi_5_mode, self.wifi_5_channel, self.wifi_5_bandwidth)

            login = ac1000f.login()
            self.console_test_modem_sig.emit('Login: <<%d>>' % (login))
            self.sleep(1)
            if login == 200:
                check = ac1000f.config_wifi_24g()
                self.console_test_modem_sig.emit('Config Wifi 2.4G: <<%d>>' % (check))
                self.sleep(1)

                check = ac1000f.config_wifi_5g()
                self.console_test_modem_sig.emit('Config Wifi 5G: <<%d>>' % (check))
                self.sleep(1)

                check = ac1000f.config_wan()
                self.console_test_modem_sig.emit('Config WAN: <<%d>>' % (check))
                self.sleep(1)

                check = ac1000f.logout()
                self.console_test_modem_sig.emit('========================')

    def run(self):
        self.obj.test_modem_btn.setEnabled(False)
        self.obj.update_data_btn.setEnabled(False)
        self.obj.config_modem_btn.setEnabled(False)
        try:
            config_modem_data = config_modem_data_db.get_config_modem_by_name(self.dev_name)
            if config_modem_data is not None:
                self.wan_account = config_modem_data[1]
                self.wan_password = config_modem_data[2]
                self.wifi24_ssid = 'FPT Telecom-%s-2.4G' % (self.dev_macwan[8:])
                self.wifi24_pass = '12345678'
                self.wifi24_mode = config_modem_data[3]
                self.wifi24_channel = config_modem_data[4]
                self.wifi24_bandwidth = config_modem_data[5]

                self.wifi5_ssid = 'FPT Telecom-%s-5G' % (self.dev_macwan[8:])
                self.wifi5_pass = '12345678'
                self.wifi5_mode = config_modem_data[6]
                self.wifi5_channel = config_modem_data[7]
                self.wifi5_bandwidth = config_modem_data[8]

                self.firmware_name = config_modem_data[9]
                self.firmware_path = config_modem_data[10]

                # kiểm tra và upgrade firmware
                if self.dev_firmware == self.firmware_name:
                    pass
                else:
                    self.upgrade_firmware()
                    # lấy thông tin thiết bị
                    self.obj.on_get_device_info()

                # Cấu hình modem
                self.config_modem()

                self.finish_flag_sig.emit('Cấu hình modem hoàn tất.')
                self.console_test_modem_sig.emit('Cấu hình modem hoàn tất.')
                self.obj.test_modem_btn.setEnabled(True)
                self.obj.update_data_btn.setEnabled(True)
                self.obj.config_modem_btn.setEnabled(True)

            else:
                self.error_sig.emit('Không tìm thấy thông tin cấu hình modem, xin kiểm tra lại.')
                self.obj.test_modem_btn.setEnabled(True)
                self.obj.update_data_btn.setEnabled(True)
                self.obj.config_modem_btn.setEnabled(True)
        except:
            self.obj.test_modem_btn.setEnabled(True)
            self.obj.update_data_btn.setEnabled(True)
            self.obj.config_modem_btn.setEnabled(True)


class ThreadGetDeviceInfo(QThread):
    console_test_modem_sig = pyqtSignal(str)

    def __init__(self, obj, parent=None):
        self.obj = obj
        QThread.__init__(self, parent=parent)

    def run(self):
        try:
            mac_lan, mac_wan = ConfigModem().get_gateway_mac()
            self.obj.dev_macwan.setText(mac_wan)
            if mac_lan != '':
                p = os.popen("pass.exe " + mac_wan).read()
                pass_ = str(p.replace("passwd:", "").replace(" ", "").replace("\n", ""))
                
                try:
                    g97rg_model = G97RG_Model('admin', pass_)
                    login = g97rg_model.login_modem()
                    if login == 200:
                        dev_name, firmware, power = g97rg_model.get_modem_info()
                        self.obj.dev_name.setText(dev_name)
                        self.obj.dev_firmware.setText(firmware)
                        self.obj.dev_power.setText(power)
                        self.obj.dev_username.setText('admin')
                        self.obj.dev_password.setText(pass_)

                    if self.obj.dev_name.text() == '---':
                        pass_ = mac_lan[2:]
                        ac100f = AC1000F('admin', pass_)
                        dev_name, power, firmware = ac100f.get_device_info()
                        self.obj.dev_name.setText(dev_name)
                        self.obj.dev_firmware.setText(firmware)
                        self.obj.dev_power.setText(power)
                        self.obj.dev_username.setText('admin')
                        self.obj.dev_password.setText(pass_)

                except:
                    self.console_test_modem_sig.emit('Không lấy được thông tin thiết bị.')
            else:
                self.obj.dev_name.setText('---')
                self.obj.dev_macwan.setText('---')
                self.obj.dev_firmware.setText('---')
                self.obj.dev_power.setText('---')
                self.obj.dev_username.setText('---')
                self.obj.dev_password.setText('---')
                self.console_test_modem_sig.emit('Không lấy được thông tin thiết bị.')
        except:
            self.obj.dev_name.setText('---')
            self.obj.dev_macwan.setText('---')
            self.obj.dev_firmware.setText('---')
            self.obj.dev_power.setText('---')
            self.obj.dev_username.setText('---')
            self.obj.dev_password.setText('---')
            self.console_test_modem_sig.emit('Không lấy được thông tin thiết bị.')


class MainWidget(QWidget):
    test_all_sig = pyqtSignal(dict)
    config_modem_sig = pyqtSignal(dict)

    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi('test_modem.ui', self)

        icon = QIcon()
        icon.addPixmap(QPixmap("logo-fpt.ico"), QIcon.Normal)
        self.setWindowIcon(icon)

        self.thread_test_all = ThreadTestAll(self)
        self.test_all_sig.connect(self.thread_test_all.on_source)
        self.thread_test_all.console_test_modem_sig.connect(self.on_update_console_test_modem)
        self.thread_test_all.progress_bar_sig.connect(self.on_update_firmware_progress)
        self.thread_test_all.download_progress_sig.connect(self.on_update_download_progress)
        self.thread_test_all.test_result_sig.connect(self.on_update_test_result)
        self.thread_test_all.finish_flag_sig.connect(self.on_finish_test)
        self.thread_test_all.error_sig.connect(self.on_error_test)

        self.thread_config_modem = ThreadConfigModem(self)
        self.config_modem_sig.connect(self.thread_config_modem.on_source)
        self.thread_config_modem.console_test_modem_sig.connect(self.on_update_console_test_modem)
        self.thread_config_modem.progress_bar_sig.connect(self.on_update_firmware_progress)
        self.thread_config_modem.finish_flag_sig.connect(self.on_finish_test)
        self.thread_config_modem.error_sig.connect(self.on_error_test)

        self.thread_get_device_info = ThreadGetDeviceInfo(self)
        self.thread_get_device_info.console_test_modem_sig.connect(self.on_update_console_test_modem)

        self.result_test_table.setSpan(0, 0, 3, 1)
        self.result_test_table.setSpan(0, 1, 1, 4)
        self.result_test_table.setSpan(0, 5, 1, 6)

        for i in [1, 2, 3, 4, 5, 8, 9, 10]:
            self.result_test_table.setSpan(1, i, 2, 1)

        self.result_test_table.setSpan(1, 6, 1, 2)

        for i in range(11):
            self.result_test_table.setColumnWidth(i, 65)

        for i in [3, 4, 5]:
            self.result_test_table.setRowHeight(i, 50)

        self.result_test_table.setItem(0, 0, MyTableWidgetItem('Số lần kiểm tra'))
        self.result_test_table.setItem(0, 1, MyTableWidgetItem('LAN'))
        self.result_test_table.setItem(0, 5, MyTableWidgetItem('WIFI'))
        self.result_test_table.setItem(1, 1, MyTableWidgetItem('Ping Time (Khi không down)'))
        self.result_test_table.setItem(1, 2, MyTableWidgetItem('Down Rate (Mbps)'))
        self.result_test_table.setItem(1, 3, MyTableWidgetItem('Ổn định khi down'))
        self.result_test_table.setItem(1, 4, MyTableWidgetItem('Kết luận'))
        self.result_test_table.setItem(1, 5, MyTableWidgetItem('Ping Time (Khi không down)'))
        self.result_test_table.setItem(1, 6, MyTableWidgetItem('Down Rate (Mbps)'))
        self.result_test_table.setItem(2, 6, MyTableWidgetItem('2.4G'))
        self.result_test_table.setItem(2, 7, MyTableWidgetItem('5G'))
        self.result_test_table.setItem(1, 8, MyTableWidgetItem('Ổn định khi down'))
        self.result_test_table.setItem(1, 9, MyTableWidgetItem('Khả năng tự kết nối lại'))
        self.result_test_table.setItem(1, 10, MyTableWidgetItem('Kết luận'))

        for i in [3, 4, 5]:
            self.result_test_table.setItem(i, 0, MyTableWidgetItem('Lần ' + str(i - 2)))


        self.test_data_table.setColumnCount(39)
        self.test_data_table.setRowCount(200)
        self.test_data_table.setWordWrap(True)

        for i in range(2, self.test_data_table.columnCount()):
            self.test_data_table.setColumnWidth(i, 50)

        self.test_data_table.setColumnWidth(0, 30)

        a = ['STT', 'MAC', 'Power', 'Kết luận', 'Ghi chú']
        a_index = 0
        for i in [0, 1, 2, 37, 38]:
            self.test_data_table.setSpan(0, i, 5, 1)
            self.test_data_table.setItem(0, i, MyTableWidgetItem(a[a_index]))
            a_index += 1


        for i in [3, 13, 23]:
            index = int((i + 7) / 10)
            self.test_data_table.setSpan(0, i, 1, 10)
            self.test_data_table.setItem(0, i, MyTableWidgetItem('Lần ' + str(index)))
            self.test_data_table.setSpan(1, i, 1, 4)
            self.test_data_table.setItem(1, i, MyTableWidgetItem('LAN'))

        self.test_data_table.setSpan(0, 33, 2, 3)
        self.test_data_table.setItem(0, 33, MyTableWidgetItem('IPTV'))
        self.test_data_table.setSpan(0, 36, 2, 1)
        self.test_data_table.setItem(0, 36, MyTableWidgetItem('VoD'))

        for i in [7, 17, 27]:
            self.test_data_table.setSpan(1, i, 1, 6)
            self.test_data_table.setItem(1, i, MyTableWidgetItem('WIFI'))

        for i in [8, 18, 28]:
            self.test_data_table.setSpan(2, i, 1, 2)
            self.test_data_table.setItem(2, i, MyTableWidgetItem('Down Rate'))

        b = [
            'Ping time (Khi không down)', 'Down rate', 'Ổn định khi down', 'Kết luận', 'Ping time (Khi không down)', 'Ổn định khi down', 'Khả năng tự kết nối lại', 'Kết luận',
            'Ping time (Khi không down)', 'Down rate', 'Ổn định khi down', 'Kết luận', 'Ping time (Khi không down)', 'Ổn định khi down', 'Khả năng tự kết nối lại', 'Kết luận',
            'Ping time (Khi không down)', 'Down rate', 'Ổn định khi down', 'Kết luận', 'Ping time (Khi không down)', 'Ổn định khi down', 'Khả năng tự kết nối lại', 'Kết luận',
            'Độ ổn định', 'Thay đổi kênh liên tục', 'Xem nhiều kênh một lúc', 'Độ ổn định'
        ]
        b_index = 0
        for i in [3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 35, 36]:
            self.test_data_table.setSpan(2, i, 3, 1)
            self.test_data_table.setItem(2, i, MyTableWidgetItem(b[b_index]))
            b_index += 1
        
        c = ['RSSI - 40dBm', 'RSSI - 55dBm', 'RSSI - 40dBm', 'RSSI - 55dBm', 'RSSI - 40dBm', 'RSSI - 55dBm']
        d = ['2.4G', '5G', '2.4G', '5G', '2.4G', '5G']
        cd_index = 0
        for i in [8, 9, 18, 19, 28, 29]:
            self.test_data_table.setItem(3, i, MyTableWidgetItem(c[cd_index]))
            self.test_data_table.setItem(4, i, MyTableWidgetItem(d[cd_index]))
            cd_index += 1

        self.test_data_table.setRowHeight(3, 50)

        for i in [6, 12, 16, 22, 26, 32, 37, 38]:
            self.test_data_table.setColumnWidth(i, 70)


        self.load_category()
        self.load_test_data()
        self.on_load_test_data()
        self.on_get_device_info()

        self.add_category_btn.clicked.connect(self.on_add_category)
        self.update_category_btn.clicked.connect(self.on_update_category)
        self.del_category_btn.clicked.connect(self.on_del_category)
        self.stop_test_btn.clicked.connect(self.on_stop_test)
        self.update_data_btn.clicked.connect(self.on_update_data)
        self.test_modem_btn.clicked.connect(self.on_test_modem)

        self.input_config_modem_btn.clicked.connect(self.on_input_config_modem)
        self.config_modem_btn.clicked.connect(self.on_config_modem)
        self.input_check_modem_btn.clicked.connect(self.on_input_check_modem)

        self.category2.currentIndexChanged.connect(self.on_load_test_data)
        self.get_data_btn.clicked.connect(self.on_load_test_data)
        self.save_data_btn.clicked.connect(self.on_save_data)
        self.del_data_btn.clicked.connect(self.on_del_data)
        self.export_excel_btn.clicked.connect(self.on_export_excel)

    def load_category(self):
        self.category1.clear()
        self.category2.clear()

        list_modem_series = modem_series_db.get_all_modem_series()
        for item in list_modem_series:
            self.category1.addItem(item[1], item[0])
            self.category2.addItem(item[1], item[0])

    def load_test_data(self):
        a = test_data_db.get_test_data()
        self.ping_gateway_edit.setText(str(a[1]))
        self.ping_fpt_edit.setText(str(a[2]))
        self.ping_24h_edit.setText(str(a[3]))
        self.ping_gg_edit.setText(str(a[4]))
        self.lan_download_url.setText(str(a[5]))
        self.wifi24_download_url.setText(str(a[6]))
        self.wifi5_download_url.setText(str(a[7]))

    def save_test_data(self):
        try:
            data = [
                self.ping_gateway_edit.text(),
                self.ping_fpt_edit.text(),
                self.ping_24h_edit.text(),
                self.ping_gg_edit.text(),
                self.lan_download_url.text(),
                self.wifi24_download_url.text(),
                self.wifi5_download_url.text()
            ]
            test_data_db.update_test_data(data)
        except:
            pass

    def on_get_device_info(self):
        self.thread_get_device_info.start()
        while not self.thread_get_device_info.isFinished():
            pass
        
    def on_input_config_modem(self):
        self.on_get_device_info()

        if self.dev_name.text() != '---':
            data = config_modem_data_db.get_config_modem_by_name(self.dev_name.text())
            if data is None:
                config_modem_data_db.create_new_config_modem_data(self.dev_name.text())

        if self.dev_name.text() in 'G-97RG3':
            self.input_config_modem_g97rg3_widget = InputConfigModem_G97RG3(self)
            self.input_config_modem_g97rg3_widget.show()
        elif self.dev_name.text() in 'G-97D2':
            self.input_config_modem_g97rg3_widget = InputConfigModem_G97D2(self)
            self.input_config_modem_g97rg3_widget.show()
        elif self.dev_name.text() in 'G-97RG6M':
            self.input_config_modem_g97rg6m_widget = InputConfigModem_G97RG6M(self)
            self.input_config_modem_g97rg6m_widget.show()
        elif self.dev_name.text() in 'G-97RG6W':
            self.input_config_modem_g97rg6w_widget = InputConfigModem_G97RG6W(self)
            self.input_config_modem_g97rg6w_widget.show()
        elif self.dev_name.text() in 'C30-401':
            self.input_config_modem_c30401_widget = InputConfigModem_C30401(self)
            self.input_config_modem_c30401_widget.show()
        else:
            

            QMessageBox.warning(self, 'Thông báo', 'Không lấy được thông tin thiết bị', QMessageBox.Yes, QMessageBox.Yes)

    def on_config_modem(self):
        self.on_get_device_info()

        self.reset_test_result_table()
        self.console_test_modem.clear()
        
        self.download_progress.setValue(0)

        dev_name = self.dev_name.text()
        if dev_name == '---':
            self.console_test_modem.append('Không lấy được thông tin thiết bị, xin kiểm tra lại.')
            QMessageBox.warning(self, 'Thông báo', 'Không lấy được thông tin thiết bị, xin kiểm tra lại.', QMessageBox.Yes, QMessageBox.Yes)
        else:
            data = {
                'dev_name': dev_name,
                'dev_macwan': self.dev_macwan.text(),
                'dev_fw': self.dev_firmware.text(),
                'dev_username': self.dev_username.text(),
                'dev_password': self.dev_password.text(),
            }
            self.config_modem_sig.emit(data)
            self.thread_config_modem.start()

    def on_input_check_modem(self):
        self.input_check_modem_widget = InputCheckModem()
        self.input_check_modem_widget.show()

    def on_add_category(self):
        text, okPressed = QInputDialog.getText(self, "Thêm lô hàng mới", "Nhập số lô hàng:", QLineEdit.Normal, "")
        if okPressed and text != '':
            lo_hang = modem_series_db.get_modem_series_by_name(text)
            if lo_hang is None:
                modem_series_db.create_new_modem_series(text)
                QMessageBox.information(self, 'Thông báo', 'Tạo lô hàng mới thành công', QMessageBox.Yes, QMessageBox.Yes)
                self.load_category()
            else:
                QMessageBox.warning(self, 'Thông báo', 'Lô hàng đã tồn tại', QMessageBox.Yes, QMessageBox.Yes)

        else:
            QMessageBox.warning(self, 'Thông báo', 'Tạo lô hàng mới không thành công', QMessageBox.Yes, QMessageBox.Yes)

    def on_update_category(self):
        name = self.category1.currentText()
        text, okPressed = QInputDialog.getText(self, "Sửa lô hàng", "Nhập số lô hàng:", QLineEdit.Normal, str(name))
        if okPressed and text != '':
            lo_hang = modem_series_db.get_modem_series_by_name(text)
            if lo_hang is None:
                modem_series_db.update_modem_series(self.category1.currentData(), text)
                QMessageBox.information(self, 'Thông báo', 'Sửa lô hàng thành công', QMessageBox.Yes, QMessageBox.Yes)
                self.load_category()
            else:
                QMessageBox.information(self, 'Thông báo', 'Lô hàng đã tồn tại', QMessageBox.Yes, QMessageBox.Yes)

        else:
            QMessageBox.warning(self, 'Thông báo', 'Sửa lô hàng không thành công', QMessageBox.Yes, QMessageBox.Yes)

    def on_del_category(self):
        msg = 'Xóa lô hàng %s ?' % (self.category1.currentText())
        buttonReply = QMessageBox.question(self, 'Thông báo', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            modem_series_db.delete_modem_series(self.category1.currentData())
            test_result_db.delete_test_result_by_category(self.category1.currentData())
            QMessageBox.information(self, 'Thông báo', 'Xóa lô hàng thành công', QMessageBox.Yes, QMessageBox.Yes)
            self.load_category()

    def on_stop_test(self):
        buttonReply = QMessageBox.question(self, 'Thông báo', 'Dừng quá trình test ?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            try:
                self.thread_test_all.stop()
                self.thread_test_all.terminate()
                self.test_modem_btn.setEnabled(True)
                self.update_data_btn.setEnabled(True)
                self.config_modem_btn.setEnabled(True)
                QMessageBox.information(self, 'Thông báo', 'Đã dừng quá trình test', QMessageBox.Yes, QMessageBox.Yes)
            except:
                QMessageBox.warning(self, 'Thông báo', 'Dừng quá trình test thất bại', QMessageBox.Yes, QMessageBox.Yes)

    def on_update_data(self):
        mac = self.dev_macwan.text()
        if mac != '---':
            list_data = list()
            list_data.append(self.dev_power.text())
            for i in [3, 4, 5]:
                for j in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    try:
                        list_data.append(self.result_test_table.item(i, j).text())
                    except:
                        list_data.append('')
            list_data.append(self.category1.currentData())
            list_data.append(mac)

            result = test_result_db.get_test_result_by_mac(mac)
            if result is None:
                test_result_db.create_new_test_result(mac)
                test_result_db.update_test_result(list_data)
            else:
                test_result_db.update_test_result(list_data)
            QMessageBox.information(self, 'Thông báo', 'Lưu kết quả test thành công', QMessageBox.Yes, QMessageBox.Yes)
        else:
            QMessageBox.warning(self, 'Thông báo', 'Lưu kết quả test thất bại.', QMessageBox.Yes, QMessageBox.Yes)

    def on_test_modem(self):
        self.save_test_data()

        self.on_get_device_info()

        self.reset_test_result_table()
        self.console_test_modem.clear()
        
        self.download_progress.setValue(0)

        dev_name = self.dev_name.text()
        if dev_name == '---':
            self.console_test_modem.append('Không lấy được thông tin thiết bị, xin kiểm tra lại.')
            QMessageBox.warning(self, 'Thông báo', 'Không lấy được thông tin thiết bị, xin kiểm tra lại.', QMessageBox.Yes, QMessageBox.Yes)
        else:
            reply = QMessageBox.question(self, 'Thông báo', "Bỏ qua phần cấu hình modem...?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                data = {
                    'dev_name': dev_name,
                    'dev_macwan': self.dev_macwan.text(),
                    'dev_fw': self.dev_firmware.text(),
                    'dev_username': self.dev_username.text(),
                    'dev_password': self.dev_password.text(),
                    'conf': False
                }
            else:
                data = {
                    'dev_name': dev_name,
                    'dev_macwan': self.dev_macwan.text(),
                    'dev_fw': self.dev_firmware.text(),
                    'dev_username': self.dev_username.text(),
                    'dev_password': self.dev_password.text(),
                    'conf': True
                }
            self.console_test_modem.append('Testing ...')
            self.test_all_sig.emit(data)
            self.thread_test_all.start()            

    def reset_test_result_table(self):
        for i in [3, 4, 5]:
            for j in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                self.result_test_table.setItem(i, j, MyTableWidgetItem(''))

    def on_update_console_test_modem(self, data):
        self.console_test_modem.append(str(data))

    def on_update_firmware_progress(self, data):
        self.download_progress.setValue(int(data['value']))
    
    def on_update_download_progress(self, data):
        current_size = data['current_size']
        total_size = data['total_size']
        speed = data['speed']
        time_remain = data['time_remain']
        percent = data['percent']

        self.download_progress.setValue(int(percent))
        self.current_size_edit.setText(str(current_size))
        self.total_size_edit.setText(str(total_size))
        self.speed_edit.setText(str(speed))
    
    def on_update_test_result(self, data):
        conn = data['conn']
        if conn == 'lan':
            if data['index'] == 1:
                self.result_test_table.setItem(3, 1, MyTableWidgetItem(str(data['ping_time'])))
                self.result_test_table.setItem(3, 2, MyTableWidgetItem(str(data['down_rate'])))
                self.result_test_table.setItem(3, 3, MyTableWidgetItem(str(data['on_dinh'])))
                self.result_test_table.setItem(3, 4, MyTableWidgetItem(str(data['ket_luan'])))
            elif data['index'] == 2:
                self.result_test_table.setItem(4, 1, MyTableWidgetItem(str(data['ping_time'])))
                self.result_test_table.setItem(4, 2, MyTableWidgetItem(str(data['down_rate'])))
                self.result_test_table.setItem(4, 3, MyTableWidgetItem(str(data['on_dinh'])))
                self.result_test_table.setItem(4, 4, MyTableWidgetItem(str(data['ket_luan'])))
            else:
                self.result_test_table.setItem(5, 1, MyTableWidgetItem(str(data['ping_time'])))
                self.result_test_table.setItem(5, 2, MyTableWidgetItem(str(data['down_rate'])))
                self.result_test_table.setItem(5, 3, MyTableWidgetItem(str(data['on_dinh'])))
                self.result_test_table.setItem(5, 4, MyTableWidgetItem(str(data['ket_luan'])))
        elif conn == 'wifi':
            if data['index'] == 1:
                self.result_test_table.setItem(3, 5, MyTableWidgetItem(str(data['ping_time'])))
                self.result_test_table.setItem(3, 6, MyTableWidgetItem(str(data['down_rate'])))
                self.result_test_table.setItem(3, 8, MyTableWidgetItem(str(data['on_dinh'])))
                self.result_test_table.setItem(3, 9, MyTableWidgetItem(str(data['ket_noi_lai'])))
                self.result_test_table.setItem(3, 10, MyTableWidgetItem(str(data['ket_luan'])))
            elif data['index'] == 2:
                self.result_test_table.setItem(4, 5, MyTableWidgetItem(str(data['ping_time'])))
                self.result_test_table.setItem(4, 6, MyTableWidgetItem(str(data['down_rate'])))
                self.result_test_table.setItem(4, 8, MyTableWidgetItem(str(data['on_dinh'])))
                self.result_test_table.setItem(4, 9, MyTableWidgetItem(str(data['ket_noi_lai'])))
                self.result_test_table.setItem(4, 10, MyTableWidgetItem(str(data['ket_luan'])))
            else:
                self.result_test_table.setItem(5, 5, MyTableWidgetItem(str(data['ping_time'])))
                self.result_test_table.setItem(5, 6, MyTableWidgetItem(str(data['down_rate'])))
                self.result_test_table.setItem(5, 8, MyTableWidgetItem(str(data['on_dinh'])))
                self.result_test_table.setItem(5, 9, MyTableWidgetItem(str(data['ket_noi_lai'])))
                self.result_test_table.setItem(5, 10, MyTableWidgetItem(str(data['ket_luan'])))
        elif conn == 'wifi5':
            if data['index'] == 1:
                ping_time = str(data['ping_time'])
                ping_time1 = self.result_test_table.item(3, 5).text()
                if ping_time == 'OK' and ping_time1 == 'OK':
                    self.result_test_table.setItem(3, 5, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(3, 5, MyTableWidgetItem('NOK'))
                
                self.result_test_table.setItem(3, 7, MyTableWidgetItem(str(data['down_rate'])))

                on_dinh = str(data['on_dinh'])
                on_dinh1 = self.result_test_table.item(3, 8).text()
                if on_dinh == 'OK' and on_dinh1 == 'OK':
                    self.result_test_table.setItem(3, 8, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(3, 8, MyTableWidgetItem('NOK'))

                self.result_test_table.setItem(3, 9, MyTableWidgetItem(str(data['ket_noi_lai'])))

                ket_luan = str(data['ket_luan'])
                ket_luan1 = self.result_test_table.item(3, 10).text()
                if ket_luan == 'OK' and ket_luan1 == 'OK':
                    self.result_test_table.setItem(3, 10, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(3, 10, MyTableWidgetItem('NOK'))
            elif data['index'] == 2:
                ping_time = str(data['ping_time'])
                ping_time1 = self.result_test_table.item(4, 5).text()
                if ping_time == 'OK' and ping_time1 == 'OK':
                    self.result_test_table.setItem(4, 5, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(4, 5, MyTableWidgetItem('NOK'))
                
                self.result_test_table.setItem(4, 7, MyTableWidgetItem(str(data['down_rate'])))

                on_dinh = str(data['on_dinh'])
                on_dinh1 = self.result_test_table.item(4, 8).text()
                if on_dinh == 'OK' and on_dinh1 == 'OK':
                    self.result_test_table.setItem(4, 8, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(4, 8, MyTableWidgetItem('NOK'))

                self.result_test_table.setItem(4, 9, MyTableWidgetItem(str(data['ket_noi_lai'])))

                ket_luan = str(data['ket_luan'])
                ket_luan1 = self.result_test_table.item(4, 10).text()
                if ket_luan == 'OK' and ket_luan1 == 'OK':
                    self.result_test_table.setItem(4, 10, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(4, 10, MyTableWidgetItem('NOK'))
            else:
                ping_time = str(data['ping_time'])
                ping_time1 = self.result_test_table.item(5, 5).text()
                if ping_time == 'OK' and ping_time1 == 'OK':
                    self.result_test_table.setItem(5, 5, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(5, 5, MyTableWidgetItem('NOK'))
                
                self.result_test_table.setItem(5, 7, MyTableWidgetItem(str(data['down_rate'])))
                on_dinh = str(data['on_dinh'])
                on_dinh1 = self.result_test_table.item(5, 8).text()
                if on_dinh == 'OK' and on_dinh1 == 'OK':
                    self.result_test_table.setItem(5, 8, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(5, 8, MyTableWidgetItem('NOK'))

                self.result_test_table.setItem(5, 9, MyTableWidgetItem(str(data['ket_noi_lai'])))

                ket_luan = str(data['ket_luan'])
                ket_luan1 = self.result_test_table.item(5, 10).text()
                if ket_luan == 'OK' and ket_luan1 == 'OK':
                    self.result_test_table.setItem(5, 10, MyTableWidgetItem('OK'))
                else:
                    self.result_test_table.setItem(5, 10, MyTableWidgetItem('NOK'))

    def on_finish_test(self, data):
        QMessageBox.information(self, 'Thông báo', str(data), QMessageBox.Yes, QMessageBox.Yes)

    def on_error_test(self, data):
        QMessageBox.warning(self, 'Thông báo', str(data), QMessageBox.Yes, QMessageBox.Yes)


    def on_load_test_data(self):
        for i in range(5, self.test_data_table.rowCount()):
            for j in range(0, self.test_data_table.columnCount()):
                self.test_data_table.setItem(i, j, MyTableWidgetItem(''))
        list_result = test_result_db.get_test_result_by_modem_series(self.category2.currentData())
        row = 5
        for result in list_result:
            self.test_data_table.setItem(row, 0, MyTableWidgetItem(str(row - 4)))
            length_result = len(result) - 1
            for i in range(0, length_result):
                if result[i] is not None:
                    self.test_data_table.setItem(row, i + 1, MyTableWidgetItem(str(result[i])))
            row += 1

    def on_save_data(self):
        try:
            for i in range(5, self.test_data_table.rowCount()):
                list_data = list()
                for j in range(2, self.test_data_table.columnCount()):
                    item = self.test_data_table.item(i, j).text()
                    list_data.append(item)
                list_data.append(self.category2.currentData())
                list_data.append(self.test_data_table.item(i, 1).text())
                test_result_db.save_test_result(list_data)
            QMessageBox.information(self, 'Thông báo', 'Lưu kết quả test thành công', QMessageBox.Yes, QMessageBox.Yes)
        except:
            QMessageBox.warning(self, 'Thông báo', 'Lưu kết quả test thất bại', QMessageBox.Yes, QMessageBox.Yes)

    def on_del_data(self):
        buttonReply = QMessageBox.question(self, 'Thông báo', 'Xóa các bản ghi đã chọn.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            index_list = []                                                          
            for model_index in self.test_data_table.selectionModel().selectedRows():       
                index = QPersistentModelIndex(model_index)         
                index_list.append(index)   

            if index_list == []:
                QMessageBox.information(self, 'Thông báo', 'Chưa chọn bản ghi', QMessageBox.Yes, QMessageBox.Yes)                           
            else:
                for index in index_list:    
                    mac = self.test_data_table.item(index.row(), 1).text()
                    test_result_db.delete_test_result(mac)                  
                    self.test_data_table.removeRow(index.row())
                QMessageBox.information(self, 'Thông báo', 'Xóa các bản ghi thành công', QMessageBox.Yes, QMessageBox.Yes)
                self.on_load_test_data()

    def on_export_excel(self):
        list_data = list()
        for i in range(5, self.test_data_table.rowCount()):
            data = list()
            for j in range(0, self.test_data_table.columnCount()):
                try:
                    item = self.test_data_table.item(i, j).text()
                    try:
                        t = float(item)
                        data.append(t)
                    except:
                        data.append(item)
                except:
                    data.append('')
            list_data.append(data)
        
        name = self.category2.currentText() + '.xlsx'
        name = name.replace('/', '').replace(' ', '_')
        file_name, _ = QFileDialog.getSaveFileName(self, "Xuất file báo cáo", str(name), "Excel Workbook (*.xlsx)")

        if file_name == '':
            pass
        else:
            write_excel_file.create_excel_file(list_data, file_name=file_name)
            QMessageBox.information(self, 'Thông báo', 'Tạo file excel thành công', QMessageBox.Yes, QMessageBox.Yes)

    def closeEvent(self, event):
        try:
            if self.thread_test_all.isRunning():
                reply = QMessageBox.question(self, 'Thông báo', "Thoát khỏi chương trình khi đang test modem...?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.thread_test_all.stop()
                    self.thread_test_all.terminate()
                    event.accept()
                else:
                    event.ignore()
        except:
            pass
import sqlite3


class TestResultDB():
    def __init__(self):
        pass

    def get_connection(self):
        return sqlite3.connect('test.db')

    def create_new_test_result(self, mac):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO test_result(mac) VALUES(?)', (mac, )
            )
            conn.commit()

    def get_test_result_by_mac(self, mac):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT mac FROM test_result WHERE mac=?', (mac, )
            )
            return cursor.fetchone()

    def update_test_result(self, data):
        query = '''
        UPDATE test_result SET power = ?,
        index10 = ?, index11 = ?, index12 = ?, index13 = ?, index14 = ?, 
        index15 = ?, index16 = ?, index17 = ?, index18 = ?, index19 = ?,
        index20 = ?, index21 = ?, index22 = ?, index23 = ?, index24 = ?, 
        index25 = ?, index26 = ?, index27 = ?, index28 = ?, index29 = ?,
        index30 = ?, index31 = ?, index32 = ?, index33 = ?, index34 = ?, 
        index35 = ?, index36 = ?, index37 = ?, index38 = ?, index39 = ?,
        so_lo_hang = ? WHERE mac = ?
        '''
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()

    def get_test_result_by_modem_series(self, so_lo_hang):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM test_result WHERE so_lo_hang = ?', (so_lo_hang, ))
            return cursor.fetchall()

    def save_test_result(self, data):
        query = '''
        UPDATE test_result SET
        power = ?, 
        index10 = ?, index11 = ?, index12 = ?, index13 = ?, index14 = ?, 
        index15 = ?, index16 = ?, index17 = ?, index18 = ?, index19 = ?, 
        index20 = ?, index21 = ?, index22 = ?, index23 = ?, index24 = ?, 
        index25 = ?, index26 = ?, index27 = ?, index28 = ?, index29 = ?, 
        index30 = ?, index31 = ?, index32 = ?, index33 = ?, index34 = ?, 
        index35 = ?, index36 = ?, index37 = ?, index38 = ?, index39 = ?, 
        iptv1 = ?, iptv2 = ?, iptv3 = ?, vod = ?, ket_luan = ?, 
        ghi_chu = ?, so_lo_hang = ? WHERE mac = ?
        '''
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()

    def delete_test_result(self, mac):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM test_result WHERE mac = ?', (mac, ))
            conn.commit()

    def delete_test_result_by_category(self, so_lo_hang):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM test_result WHERE so_lo_hang = ?', (so_lo_hang, ))


class ModemSeriesDB():
    def __init__(self):
        pass

    def get_connection(self):
        return sqlite3.connect('test.db')

    def get_all_modem_series(self):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM lo_hang')
            return cursor.fetchall()

    def create_new_modem_series(self, ten_lo_hang):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO lo_hang(ten_lo_hang) VALUES(?)', (ten_lo_hang, ))
            conn.commit()

    def update_modem_series(self, id, ten_lo_hang):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE lo_hang SET ten_lo_hang = ? WHERE id = ?', (ten_lo_hang, id))
            conn.commit()

    def delete_modem_series(self, id):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM lo_hang WHERE id = ?', (id, ))
            conn.commit()

    def get_modem_series_by_name(self, ten_lo_hang):
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM lo_hang WHERE ten_lo_hang = ?', (ten_lo_hang, ))
            return cursor.fetchone()


class ConfigModemDataDB():
    def __init__(self):
        pass

    def get_connection(self):
        return sqlite3.connect('test.db')

    def create_new_config_modem_data(self, modem_name):
        query = '''INSERT INTO config_modem_data(modem_name, 
        wifi24_mode, wifi24_channel, wifi24_bandwidth,
        wifi5_mode , wifi5_channel , wifi5_bandwidth) 
        VALUES (?, ?, ?, ?, ?, ?, ?)'''
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    query, (modem_name, '0', '0', '0', '0', '0', '0'))
                return True
            except:
                return False

    def get_config_modem_by_name(self, modem_name):
        query = 'SELECT * FROM config_modem_data WHERE modem_name = ?'
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, (modem_name, ))
            return cursor.fetchone()

    def update_config_modem_data(self, data):
        query = '''
            UPDATE config_modem_data SET
            wan_account = ?, wan_password = ?,
            wifi24_mode = ?, wifi24_channel = ?, wifi24_bandwidth = ?,
            wifi5_mode = ?, wifi5_channel = ?, wifi5_bandwidth = ?,
            firmware_name = ?, firmware_path = ?
            WHERE modem_name = ?
        '''
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, data)
                return True
            except:
                return False


class CheckTestDataDB():
    def __init__(self):
        pass

    def get_connection(self):
        return sqlite3.connect('test.db')

    def get_check_test_data(self):
        query = 'SELECT * FROM check_test_data'
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchone()

    def update_check_test_data(self, data):
        query = '''
            UPDATE check_test_data SET
            lan_time1 = ?, lan_time2 = ?, lan_time3 = ?, lan_time4 = ?,
            lan_loss1 = ?, lan_loss2 = ?, lan_loss3 = ?, lan_loss4 = ?,
            wifi_time1 = ?, wifi_time2 = ?, wifi_time3 = ?, wifi_time4 = ?,
            wifi_loss1 = ?, wifi_loss2 = ?, wifi_loss3 = ?, wifi_loss4 = ?,
            lan_speed = ?, wifi24_speed = ?, wifi5_speed = ?
            WHERE id = 1
        '''
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, data)


class TestDataDB():
    def __init__(self):
        pass

    def get_connection(self):
        return sqlite3.connect('test.db')

    def get_test_data(self):
        query = 'SELECT * FROM test_data'
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchone()

    def update_test_data(self, data):
        query = '''UPDATE test_data SET 
            ping_gw = ?, ping_fpt = ?, ping_24h = ?, ping_gg = ?, 
            lan_download_url = ?, wifi24_download_url = ?, wifi5_download_url = ?
            WHERE id = 1
        '''
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, data)
                return True
            except:
                return False


test_result_db = TestResultDB()
modem_series_db = ModemSeriesDB()
config_modem_data_db = ConfigModemDataDB()
check_test_data_db = CheckTestDataDB()
test_data_db = TestDataDB()


if __name__ == '__main__':
    config_modem_data = config_modem_data_db.get_config_modem_by_name(
        'G-97RG3')
    print(config_modem_data)
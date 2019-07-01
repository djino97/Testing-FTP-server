import unittest, ftplib
from ftplib import FTP
from urllib.parse import urlparse
import time, os


class LoginTest(unittest.TestCase):
    """
    Tests log in with an anonymous user and log in
    with a unique username and password.
    """

    def setUp(self):
        """
        FTP-server connection.
        :return:open connection instance
        """
        url = urlparse("ftp://speedtest.tele2.net")
        self.ftp = FTP(url.netloc)
        return self.ftp

    def test_login_anonymous(self):
        self.assertEqual("230 Login successful.", self.ftp.login())

    def test_login_user(self):
        try:
            self.ftp.login('username', 'user_password')
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 This FTP server is anonymous only.", str(error_upload))

    def tearDown(self):
        """
        Closing connection with FTP server.
        :return:
        """
        self.assertEqual("221 Goodbye.", self.ftp.quit())


class ModifyContentFolders(unittest.TestCase):
    """
    Creating directories and deleting files from the server.
    """

    def setUp(self):
        self.ftp = LoginTest().setUp()

    def test_create_root_folder_without_login(self):
        """
        Creating a new folder in the root folder of the server without logging in.
        :return:
        """
        try:
            self.ftp.mkd('/pictures')
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 Please login with USER and PASS.", str(error_upload))

    def test_create_root_folder(self):
        """
        Creating a new folder in the root folder of the server after logging in.
        :return:
        """
        self.ftp.login()
        try:
            self.ftp.mkd('/pictures')
        except ftplib.error_perm as error_upload:
            self.assertEqual("550 Permission denied.", str(error_upload))

    def test_create_upload_folder_without_login(self):
        """
        Creating a new folder in the "/upload" folder of the server without logging in.
        :return:
        """
        try:
            self.ftp.cwd('upload')
            self.ftp.mkd('/pictures')
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 Please login with USER and PASS.", str(error_upload))

    def test_create_upload_folder(self):
        """
        Creating a new folder in the "/upload" folder of the server after logging in.
        :return:
        """
        self.ftp.login()
        self.ftp.cwd('upload')
        try:
            self.ftp.mkd('/pictures')
        except ftplib.error_perm as error_upload:
            self.assertEqual("550 Permission denied.", str(error_upload))

    def test_delete_file_without_login(self):
        """
        Delete file in server root folder without logging in.
        :return:
        """
        try:
            self.ftp.delete('1GB.zip')
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 Please login with USER and PASS.", str(error_upload))

    def test_delete_file(self):
        """
        Delete file in server root folder after logging in.
        :return:
        """
        self.ftp.login()
        try:
            self.ftp.delete('1GB.zip')
        except ftplib.error_perm as error_upload:
            self.assertEqual("550 Permission denied.", str(error_upload))

    def tearDown(self):
        self.assertEqual("221 Goodbye.", self.ftp.quit())


def path_file_download():
    """
    Sets the desired file to download.
    :return:
    out_path - path where the file will be saved
    filename - name file on the server
    """
    filename = '100MB.zip'
    out_path = r'D:\\{0}'.format(filename)
    return out_path, filename


def write_on_pc(ftp, path, file):
    """
    Function for downloading a file from the server.
    Displays in console download speed.

    :param ftp: open connection instance
    :param path: path where the file will be saved
    :param file: name file on the server
    :return:
    """
    size = ftp.size('/100MB.zip')
    start = time.time()
    with open(path, 'wb') as f:
        ftp.retrbinary('RETR ' + file, f.write, 512)
        end = time.time()

        speed = size // (1024 * (end - start))
    print("Download speed - %s KB/s" % speed)


class DownloadTest(unittest.TestCase):
    """
    Testing file download from FTP server.
    """

    def setUp(self):
        self.ftp = LoginTest().setUp()
        self.out_path, self.filename = path_file_download()

    def test_download_file_without_login(self):
        """
        Download file without logging in.
        :return:
        """
        try:
            write_on_pc(self.ftp, self.out_path, self.filename)
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 Please login with USER and PASS.", str(error_upload))

    def test_download_file(self):
        """
        Download file after logging in.
        :return:
        """
        self.ftp.login()
        write_on_pc(self.ftp, self.out_path, self.filename)

    def tearDown(self):
        self.assertEqual("221 Goodbye.", self.ftp.quit())


class TransitionFolder(unittest.TestCase):
    """
    Testing transition between folders.
    """
    def setUp(self):
        self.ftp = LoginTest().setUp()

    def test_transition_into_folder_without_login(self):
        """
        Moving to a "/upload" folder without logging in.
        :return:
        """
        try:
            self.ftp.cwd("/upload")
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 Please login with USER and PASS.", str(error_upload))

    def test_transition_into_folder(self):
        """
        Moving to a "/upload" folder after logging in.
        :return:
        """
        self.ftp.login()
        self.ftp.cwd("/upload")
        self.assertEqual("/upload", self.ftp.pwd())

    def test_transition_from_folder(self):
        """
        Moving to a "/upload" folder after logging in and moving to a root folder server.
        :return:
        """
        self.ftp.login()
        self.ftp.cwd("/upload")
        self.ftp.cwd("/")
        self.assertEqual("/", self.ftp.pwd())

    def tearDown(self):
        self.assertEqual("221 Goodbye.", self.ftp.quit())


def path_file_upload():
    """
    Sets the desired file to upload to server.
    :return:
    """
    file_name = 'upload_100MB.zi'
    input_file = r'D:\\{0}'.format(file_name)
    total_size = os.path.getsize(input_file)
    return total_size, input_file, file_name


def write_on_ftp(ftp, path, size, file_name):
    """
    Function for uploading a file to the server.
    Displays in console download speed.
    :param ftp: open connection instance
    :param path: path where the file will be saved
    :param size: file size
    :param file_name: file name to be uploaded
    :return:
    """
    start = time.time()
    with open(path, 'rb') as f:
        ftp.storbinary('STOR ' + file_name, f, 1024)
        speed_upload = size // (1024 * (time.time() - start))
    print("Upload speed - %s KB/s" % speed_upload)


class UploadTest(unittest.TestCase):
    def setUp(self):
        self.ftp = LoginTest().setUp()
        self.total_size, self.input_file, self.file_name = path_file_upload()

    def test_root_folder_without_login(self):
        """
        File upload to the the server without logging in.
        :return:
        """
        try:
            write_on_ftp(self.ftp, self.input_file, self.total_size,  self.file_name)
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 Please login with USER and PASS.", str(error_upload))

    def test_upload_folder_without_login(self):
        """
        File upload to the rout directory of the server without logging in.
        :return:
        """
        try:
            self.ftp.cwd('upload')
            write_on_ftp(self.ftp, self.input_file, self.total_size,  self.file_name)
        except ftplib.error_perm as error_upload:
            self.assertEqual("530 Please login with USER and PASS.", str(error_upload))

    def test_upload_root_folder(self):
        """
        File upload to the server after logging in.
        :return:
        """
        self.ftp.login()
        try:
            write_on_ftp(self.ftp, self.input_file, self.total_size,  self.file_name)
        except ftplib.error_perm as error_upload:
            self.assertEqual("553 Could not create file.", str(error_upload))

    def test_upload_folder(self):
        """
        File upload to the "/upload" directory of the server after logging in.
        :return:
        """
        self.ftp.login()
        self.ftp.cwd('upload')
        write_on_ftp(self.ftp, self.input_file, self.total_size, self.file_name)

    def test_delete_upload_file(self):
        """
        Check file deletion after upload to "/upload" directory.
        :return:
        """
        self.ftp.login()
        self.ftp.cwd('upload')
        try:
            self.ftp.size('/upload/{0}').format(self.file_name)
        except ftplib.error_perm as error_upload:
            self.assertEqual("550 Could not get file size.", str(error_upload))

    def tearDown(self):
        self.assertEqual("221 Goodbye.", self.ftp.quit())


if __name__ == '__main__':
    unittest.main()

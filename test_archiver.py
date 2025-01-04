import pytest, os, time
from archiver import Archiver
from contacts_model import Contact


@pytest.fixture(autouse=True)
def init_test():
    Contact.load_db()
    return

def test_init():
    archiver = Archiver.get()
    archiver.run()
    assert archiver.isRunning == True

def test_load():
    assert len(Contact.all()) == 47

def test_write_to_file():
    archiver = Archiver.get()
    archiver.write_to_file()
    file_path = 'tmp/archive.json'
    assert os.path.exists(file_path), f"File {file_path} does not exist"
    assert os.path.getsize(file_path)>5000, f"File {file_path} is too small"

def test_run():
    archiver = Archiver.get()
    archiver.run()
    start_time = time.time()
    timeout = 10
    while archiver.isRunning:
        assert time.time() - start_time < timeout, f"Timeout waiting for archiver to start running"
        time.sleep(0.1)  # Sleep briefly to avoid busy waiting
    assert archiver.isRunning == False

   
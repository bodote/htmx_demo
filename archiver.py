import json,threading,time,os
from contacts_model import Contact

class Archiver:
    file_path = 'tmp/archive.json'

    def __init__(self):
        self.isRunning = False
        self.progress = float(1.0)
        return
    @classmethod
    def get(cls):
        return cls()
    
    def run(self):
        assert Contact.count() > 0
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            print(f"File {self.file_path} has been deleted")
        thread = threading.Thread(target=self.write_to_file)
        thread.start()
        return
    
    def write_to_file(self):
        self.isRunning = True
        assert Contact.count() > 0
        with open(self.file_path, 'w') as archive_file:
            archive_file.write("[")
            for index,contact in enumerate(Contact.all()):
                time.sleep(0.03)
                contact_json = json.dumps(contact.to_dict())
                self.progress = (index + 1) / (Contact.count())
                if index < Contact.count() - 1:
                    archive_file.write(contact_json +",\n")
                    archive_file.flush()
                    os.fsync(archive_file.fileno())
                else:
                    archive_file.write(contact_json )
            archive_file.write("]")
            self.progress = 1.0
            self.isRunning = False
        return
    
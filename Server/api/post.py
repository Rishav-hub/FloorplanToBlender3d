from shared_variables import shared_variables
from api.api import Api
from process.create import Create
from config.file_handler import FileHandler

class Post(Api):
    
    def create(self, *args):
        """Create new specific file name/id and hash"""
        tmp_id = None

        while self.shared.id_exist(tmp_id) or tmp_id is None: 
            tmp_id = self.shared.id_generator()
        
        pair = (tmp_id,self.shared.hash_generator(tmp_id), False)
        self.shared.all_ids.append(pair)

        return str(pair)

    def remove(self, api_ref, data, *args):
        """Remove existing file id"""
        fs = FileHandler()
        # Target
        fs.remove("./storage/target/"+data["id"]+".blend")
        # Data
        fs.remove("./storage/data/"+data["id"]+"0/")
        # Image
        fs.remove(self.shared.get_image_path(data["id"]))
        # Objects
        fs.remove("./storage/objects/"+data["id"]+"*") # TODO: fix this!
        return "Removed id!"

    def transform(self, api_ref, data, *args):
        """Transform Image to Object"""
        _id = self.shared.get_id(data['id'])
        if _id is not None and _id[2]:
            if(data['format'] in self.shared.supported_blender_formats):
                Create(data=data, shared_variables = self.shared).start()
                message = "TransformProcess started! Query Process Status for more Information."
            else:
                message = "Format not supported!"
        else:
            message = "File doesn't exist!"
            self.shared.bad_client_event(self.client)
        return message

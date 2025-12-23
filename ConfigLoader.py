import os

class ConfigLoader:

    @staticmethod
    def load_config(file_path):
        """
        get file and return the Inf as a dict
        """

        # 1. default
        config = {
            "message": "",
            "maximum_msg_size": 1024,
            "window_size": 1,
            "timeout": 5,
            "dynamic message size": False
        }

        # Check if file already exist
        if not os.path.exists(file_path):
            print(f"Warning: Config file '{file_path}' not found. Using defaults.")
            return config

        #new file
        try:
            with open(file_path, 'r') as f:
                for line in f: #in every loop it will take the next line from the file(python magic)

                    # cleaning
                    line = line.strip()

                    # checking
                    # if empty or not contain : - good - so continue
                    if not line or ":" not in line:
                        continue

                    # getting (key) and (value)
                    key, value = line.split(":",1)

                    # relevant value
                    # remove: -spaces - "" - '
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    # put in the dict by right order
                    # Distinguish between each different part
                    if key == "message":
                        config["message"] = str(value)

                    elif key == "maximum_msg_size":
                        config["maximum_msg_size"] = int(value)

                    elif key == "window_size":
                        config["window_size"] = int(value)

                    elif key == "timeout":
                        config["timeout"] = int(value)

                    elif key == "dynamic message size":
                        config["dynamic message size"] = (value.lower() == "true") # just "bool" will pass everything

            print(f"Config loaded from {file_path}")
            return config

        except Exception as e:
            print(f"Error loading config: {e}")
            return config



if __name__ == "__main__":

    conf = ConfigLoader.load_config("client_config.txt")
    print(conf)
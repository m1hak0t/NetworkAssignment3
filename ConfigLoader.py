import inspect
import os

class ConfigLoader:

    @staticmethod
    def _get_manual_input(ifserver : bool):

        try :
            # Requirements for specific variables [cite: 69, 70, 71]
            print("\n--- Manual Input Mode ---")

            if ifserver:
                print("Detected caller: SERVER")
                # Logic for server
                return {
                    "maximum_msg_size": int(input("Enter maximum message size (bytes): ")),  # [cite: 70]
                    "timeout": int(input("Enter timeout (seconds): ")),  # [cite: 71]
                    "dynamic message size": input("Dynamic message size? (True/False): ").lower(), # [cite: 71]
                    "sabotage_mode": input("Do you want to sabotage packages? (True/False): ").lower(),
                    "sabotage_probability": input("Enter the probability of sabotage packages? (0.0-1.0): ")
                }

            if ifserver == False:

                print("Detected caller: CLIENT")
                # Logic for client
                return {
                    "message": input("Enter the desired message: "),  # [cite: 69]
                    "window_size": int(input("Enter window size (integer): ")),  # [cite: 71]
                    "timeout": int(input("Enter timeout (seconds): ")),  # [cite: 71]

                }

        except Exception as e:
            print("Something is incorrect, contact Shira and Michael for support, but for now just try one more time")
            ConfigLoader._get_manual_input(ifserver)


    @staticmethod
    def load_config(file_path, ifserver : bool):
        """
        get file and return the Inf as a dict
        """

        """
                Always asks the user to choose between a file or manual input.
                """
        print("--- Configuration Setup ---")
        print("1. Use default config file (server_config.txt)")
        print("2. Enter values manually")

        choice = input("Select an option (1 or 2): ").strip()

        if choice == "1" :

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
                print(f"Warning: Config file '{file_path}' not found. Add manualy.")
                return ConfigLoader._get_manual_input(ifserver)

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
                        elif key == "sabotage_mode":
                            config["sabotage_mode"] = True if value.lower() == "true" else False
                        elif key == "sabotage_probability":
                            config["sabotage_probability"] = value

                print(f"Config loaded from {file_path}")
                return config

            except Exception as e:
                print(f"Error loading config: {e}")
                return config
        if choice == "2" :
            return ConfigLoader._get_manual_input(ifserver)


if __name__ == "__main__":

    conf = ConfigLoader.load_config("client_config.txt")
    print(conf)
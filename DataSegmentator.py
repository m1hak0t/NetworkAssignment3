from logging import exception

from ConfigLoader import ConfigLoader


class DataSegmentator:
    def __init__(self, filename, config : ConfigLoader):
        self.config = config
        self.message = self.config["message"]
        self.timeout = self.config["timeout"]
        self.encoded_data = self.message.encode("utf-8")
        print(self.encoded_data.hex())
        self.current_start = 0
        self.current_end = 0
        self.segment_counter =0
        self.segments = []


    def next(self, step):
        #Move exactly step bytes further
        self.current_start = self.current_end
        self.current_end = self.current_start + step
        self.segment_counter += 1
        #If there is data -> inerate

        if self.current_end < len(self.encoded_data):
            segment = self.encoded_data[self.current_start:self.current_end]
            if segment :
                self.segments.append((self.current_start, self.current_end))
                return segment
        else:
            segment = self.encoded_data[self.current_start:len(self.encoded_data)]
            if segment:
                self.segments.append((self.current_start, self.current_end))
                return segment

    def get(self, index):
        if len(self.segments) > index:
            first_index = self.segments[index][0]
            second_index = self.segments[index][1]
            return self.encoded_data[first_index:second_index]
        else:
            print("This segment does not exist")
            return None

    def get_seq_number(self):
        return self.segment_counter

    def isfinished(self):
        return self.current_start >= len(self.encoded_data)


if __name__ == "__main__":
    conf = DataSegmentator("client_config.txt")
    raw = b""
    while True:
        user_input = input("Enter the next segment size")
        size = int(user_input)
        print(conf.next(size))
        if size == 0 :
            break
    while True:
        user = int(input("Enter the index"))
        print(conf.get(user))


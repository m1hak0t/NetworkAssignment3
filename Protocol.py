#This class is intended to define a clear protocol between the client and the server
class Protocol:

    MSG_SYN = "SYN"
    MSG_ACK = "ACK"
    MSG_SYN_ACK = "SYN-ACK"
    MSG_DATA = "DATA"
    MSG_SIZE_REQ = "SIZE_REQ"
    MSG_SIZE_RES = "SIZE_RES"

    #separation between the datas - we can change just this obj instand the code
    DELIMITER = "|"

    #Get parts and return a message - according to the protocol
    @staticmethod
    def make_packet(msg_type, seq_num=0, payload=""):

        msg = msg_type + Protocol.DELIMITER + str(seq_num) + Protocol.DELIMITER + payload
        msg_binary =  msg.encode("utf-8")
        return msg_binary

        pass

    #getting the massage and return Inf parts - according to the protocol
    @staticmethod
    def parse_packet(message):

        msg_from_binary = message.decode("utf-8")
        parts = msg_from_binary.split(Protocol.DELIMITER, 2)

        msg_type = parts[0]
        seq_num = int(parts[1])
        payload = parts[2]
        return msg_type, seq_num, payload

        pass
#This class is intended to define a clear protocol between the client and the server
class Protocol:

    MSG_SYN = "SYN"
    MSG_ACK = "ACK"
    MSG_SYN_ACK = "SYN-ACK"
    MSG_DATA = "DATA"
    MSG_REQ_SIZE = "REQ_SIZE" #for client
    MSG_SIZE_RESP = "SIZE_RES" #for server


    #separation between the datas - we can change just this obj instand the code
    DELIMITER = "|"

    @staticmethod
    def make_packet(msg_type, seq_num=0, payload=""):
        # Добавляем \n как разделитель пакетов
        msg = f"{msg_type}{Protocol.DELIMITER}{seq_num}{Protocol.DELIMITER}{payload}\n"
        return msg.encode("utf-8")


    @staticmethod
    def get_packet_from_str(packet_str):
        # Парсим строку, убирая лишние пробелы/символы конца строки
        parts = packet_str.strip().split(Protocol.DELIMITER, 2)
        return parts[0], int(parts[1]), parts[2]

    #Get parts and return a message - according to the protocol

    #getting the massage and return Inf parts - according to the protocol
    @staticmethod
    def get_packet(message):

        msg_from_binary = message.decode("utf-8")
        parts = msg_from_binary.split(Protocol.DELIMITER, 2)

        msg_type = parts[0]
        seq_num = int(parts[1])
        payload = parts[2]
        return msg_type, seq_num, payload

        pass
import sys
import os

# הקסם: הוספת התיקייה "אחת למעלה" לנתיב החיפוש של פייתון
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Protocol import Protocol

def run_protocol_test():
    print("=== Starting Protocol Logic Test ===")

    # 1. Setup Test Data
    # We define the data we want to send.
    # Note: We intentionally include the delimiter '|' inside the payload
    # to ensure our split logic handles it correctly without breaking.
    msg_type_in = Protocol.MSG_DATA
    seq_num_in = 12345
    payload_in = "Hello World | This contains a pipe symbol | End of message"

    print("[Step 1] Original Data: Type={msg_type_in}, Seq={seq_num_in}, Payload='{payload_in}'")

    # 2. Simulation: Client Side (Packing)
    # Convert the data into bytes using make_packet
    try:
        encoded_packet = Protocol.make_packet(msg_type_in, seq_num_in, payload_in)
        print(f"[Step 2] Encoded (sent over network): {encoded_packet}")
    except Exception as e:
        print(f"Error during make_packet: {e}")
        return

    # 3. Simulation: Server Side (Parsing)
    # Decode the bytes back into variables using get_packet
    try:
        msg_type_out, seq_num_out, payload_out = Protocol.get_packet(encoded_packet)
    except Exception as e:
        print(f"Error during get_packet: {e}")
        return

    # 4. Verification
    # Check if the received data matches exactly what we sent
    print(f"[Step 3] Decoded Data: Type={msg_type_out}, Seq={seq_num_out}, Payload='{payload_out}'")

    # Verify Sequence Number type (must be int, not str)
    if not isinstance(seq_num_out, int):
        print(" FAILED: Sequence number is not an Integer!")
        return

    # Verify Content
    if (msg_type_in == msg_type_out and
        seq_num_in == seq_num_out and
        payload_in == payload_out):
        print("\n TEST PASSED: Protocol logic is solid.")
    else:
        print("\n TEST FAILED: Data mismatch.")

if __name__ == "__main__":
    run_protocol_test()
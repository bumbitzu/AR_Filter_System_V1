from main import KeySender

def test_key_sender():
    print("Testing KeySender...")
    key_sender = KeySender(hold_ms=50, delay_ms=80)

    # Test single key press
    print("Pressing 'ctrl+1'...")
    key_sender.send_sequence(["ctrl+1"])

    print("Pressing 'ctrl+2'...")
    key_sender.send_sequence(["ctrl+2"])

if __name__ == "__main__":
    test_key_sender()
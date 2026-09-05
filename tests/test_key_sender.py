"""
Script de testare pentru KeySender
Testeaza functionalitatea de simulare a apasarii tastelor
Folosit pentru debugging si verificarea corecta a combinatiilor de taste
"""
from main import KeySender

def test_key_sender():
    """
    Functie de test pentru KeySender
    Testeaza apasarea combinatiilor ctrl+1 si ctrl+2
    """
    print("Testare KeySender...")
    
    # Creeaza instanta KeySender cu setari standard
    key_sender = KeySender(hold_ms=50, delay_ms=80)

    # Test 1: Apasare combinatie ctrl+1
    print("Apelez 'ctrl+1'...")
    key_sender.send_sequence(["ctrl+1"])

    # Test 2: Apasare combinatie ctrl+2
    print("Apelez 'ctrl+2'...")
    key_sender.send_sequence(["ctrl+2"])

if __name__ == "__main__":
    """
    Punct de intrare pentru testare
    Ruleaza testele de simulare a tastelor
    """
    test_key_sender()
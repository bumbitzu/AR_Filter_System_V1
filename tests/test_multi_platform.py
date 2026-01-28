"""
Script de testare pentru sistemul multi-platform de tipping
Verifică că toate cele 3 platforme funcționează corect
"""
import time
import requests
import sys


class MultiPlatformTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.test_results = {
            'chaturbate': [],
            'stripchat': [],
            'camsoda': []
        }
    
    def print_header(self, text):
        """Afișează un header frumos"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def test_platform(self, platform, amount, username):
        """Testează o platformă specifică"""
        try:
            # Trimite request de trigger
            trigger_url = f"{self.base_url}/trigger/{platform}/{amount}/{username}"
            response = requests.get(trigger_url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {platform.upper()}: Trigger successful ({amount} tokens from {username})")
                
                # Verifică dacă events endpoint returnează datele
                time.sleep(0.5)
                events_url = f"{self.base_url}/events/{platform}"
                events_response = requests.get(events_url, timeout=5)
                
                if events_response.status_code == 200:
                    data = events_response.json()
                    events = data.get('events', [])
                    
                    if events:
                        print(f"   📦 Events endpoint returned {len(events)} event(s)")
                        self.test_results[platform].append({
                            'status': 'success',
                            'amount': amount,
                            'username': username
                        })
                    else:
                        print(f"   ⚠️  Events endpoint returned empty list (events already consumed)")
                        self.test_results[platform].append({
                            'status': 'consumed',
                            'amount': amount,
                            'username': username
                        })
                else:
                    print(f"❌ {platform.upper()}: Events endpoint failed (status {events_response.status_code})")
                    self.test_results[platform].append({'status': 'failed'})
            else:
                print(f"❌ {platform.upper()}: Trigger failed (status {response.status_code})")
                self.test_results[platform].append({'status': 'failed'})
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {platform.upper()}: Cannot connect to server. Is mock_server.py running?")
            self.test_results[platform].append({'status': 'connection_error'})
        except Exception as e:
            print(f"❌ {platform.upper()}: Error - {str(e)}")
            self.test_results[platform].append({'status': 'error', 'message': str(e)})
    
    def run_full_test(self):
        """Rulează teste pentru toate platformele și toate filtrele"""
        self.print_header("🧪 AR FILTER SYSTEM - MULTI-PLATFORM TEST")
        
        # Verifică dacă serverul este online
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print(f"\n✅ Mock server is running at {self.base_url}")
            else:
                print(f"\n⚠️  Mock server responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"\n❌ ERROR: Cannot connect to {self.base_url}")
            print("   Please start the mock server first:")
            print("   python tests/mock_server.py")
            return False
        
        # Test 1: Sparkles Filter (33 tokens)
        self.print_header("Test 1: Sparkles Filter (33 tokens)")
        self.test_platform('chaturbate', 33, 'ChatUser1')
        time.sleep(0.5)
        self.test_platform('stripchat', 33, 'StripUser1')
        time.sleep(0.5)
        self.test_platform('camsoda', 33, 'CamUser1')
        
        # Test 2: Big Eyes Filter (99 tokens)
        self.print_header("Test 2: Big Eyes Filter (99 tokens)")
        self.test_platform('chaturbate', 99, 'ChatUser2')
        time.sleep(0.5)
        self.test_platform('stripchat', 99, 'StripUser2')
        time.sleep(0.5)
        self.test_platform('camsoda', 99, 'CamUser2')
        
        # Test 3: Cyber Mask Filter (200 tokens)
        self.print_header("Test 3: Cyber Mask Filter (200 tokens)")
        self.test_platform('chaturbate', 200, 'ChatUser3')
        time.sleep(0.5)
        self.test_platform('stripchat', 200, 'StripUser3')
        time.sleep(0.5)
        self.test_platform('camsoda', 200, 'CamUser3')
        
        # Print summary
        self.print_summary()
        return True
    
    def print_summary(self):
        """Afișează un sumar al rezultatelor"""
        self.print_header("📊 TEST SUMMARY")
        
        total_tests = 0
        successful_tests = 0
        
        for platform, results in self.test_results.items():
            platform_success = sum(1 for r in results if r.get('status') in ['success', 'consumed'])
            total_tests += len(results)
            successful_tests += platform_success
            
            status_emoji = "✅" if platform_success == len(results) else "⚠️"
            print(f"\n{status_emoji} {platform.upper()}: {platform_success}/{len(results)} tests passed")
        
        print(f"\n{'='*60}")
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"Overall Success Rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"{'='*60}\n")
        
        if success_rate == 100:
            print("🎉 All tests passed! Your multi-platform system is working perfectly!")
        elif success_rate >= 66:
            print("⚠️  Some issues detected. Check the errors above.")
        else:
            print("❌ Multiple failures detected. Please verify:")
            print("   1. Mock server is running (python tests/mock_server.py)")
            print("   2. All platform listeners are properly configured")
            print("   3. No firewall blocking localhost connections")


def main():
    """Main function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        AR FILTER SYSTEM - MULTI-PLATFORM TESTER              ║
║                                                              ║
║  This script tests the integration of all 3 platforms:       ║
║  • Chaturbate                                                ║
║  • Stripchat                                                 ║
║  • Camsoda                                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    tester = MultiPlatformTester()
    
    # Verifică dacă server-ul rulează
    print("🔍 Checking if mock server is running...")
    time.sleep(1)
    
    # Rulează testele
    success = tester.run_full_test()
    
    if success:
        print("\n💡 Next steps:")
        print("   1. Start main application: python main.py")
        print("   2. Open browser: http://127.0.0.1:5000")
        print("   3. Click test links to trigger filters")
        print("   4. Watch the filters activate in real-time!")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

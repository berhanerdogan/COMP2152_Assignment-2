"""
Unit Tests for Assignment 2 — Port Scanner
"""

import unittest

from assignment2_101591316 import PortScanner, common_ports


class TestPortScanner(unittest.TestCase):

    def test_scanner_initialization(self):

        """Test that PortScanner initializes with correct target and empty results list."""
        
        scanner = PortScanner("127.0.0.1")
        target = scanner.target
        realTaret = "127.0.0.1"
        results = scanner.scan_results

        self.assertIsInstance(scanner, PortScanner)
        self.assertEqual(target, realTaret)
        self.assertFalse(results)

    def test_get_open_ports_filters_correctly(self):

        """Test that get_open_ports returns only Open ports."""

        scanner = PortScanner("127.0.0.1")
        scanner.scan_results = [
            (22, "Open", "SSH"),
            (23, "Closed", "Telnet"),
            (80, "Open", "HTTP")
        ]
        result = scanner.get_open_ports()
        self.assertEqual(len(result), 2)

    def test_common_ports_dict(self):

        """Test that common_ports dictionary has correct entries."""

        http = "HTTP"
        ssh = "SSH"

        self.assertEqual(common_ports[80], http)
        self.assertEqual(common_ports[22], ssh)


    def test_invalid_target(self):
        
        """Test that setter rejects empty string target."""
        
        scanner = PortScanner("127.0.0.1")
        with self.assertRaises(ValueError):
            scanner.target = ""
        self.assertEqual(scanner.target, "127.0.0.1")


if __name__ == "__main__":
    unittest.main()

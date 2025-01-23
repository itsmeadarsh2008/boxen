import unittest
import os
import shutil
from src.boxen.boxen import boxen, CLI_BOXES


class TestBoxen(unittest.TestCase):
    def _print_box(self, test_name, content):
        """Helper to print boxes if PRINT_BOXES env var is set"""
        if os.getenv("PRINT_BOXES") == "1":
            print(f"\n{test_name}:\n{content}")

    def test_basic_output(self):
        result = boxen("Hello")
        self._print_box("Basic Output", result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)

    def test_border_styles(self):
        for style in CLI_BOXES:
            with self.subTest(style=style):
                result = boxen("Test", {"borderStyle": style})
                self._print_box(f"Border Style: {style}", result)
                if style == "none":
                    self.assertNotIn(CLI_BOXES["single"]["topLeft"], result)
                else:
                    self.assertIn(CLI_BOXES[style]["topLeft"], result)

    def test_custom_border(self):
        custom = {
            "topLeft": "A",
            "topRight": "B",
            "bottomRight": "C",
            "bottomLeft": "D",
            "horizontal": "E",
            "vertical": "F",
        }
        result = boxen("Test", {"borderStyle": custom, "width": 7})
        self._print_box("Custom Border", result)
        self.assertIn("AEEEEEB", result)  # Top border
        self.assertIn("DEEEEEC", result)  # Bottom border
        self.assertIn("FTest F", result)  # Content line

    def test_padding(self):
        result = boxen("Test", {"padding": 1})
        self._print_box("Padding Test", result)
        lines = result.split("\n")
        content_line = lines[1]
        self.assertTrue(content_line.startswith("│ "))
        self.assertTrue(content_line.endswith(" │"))

    def test_margins(self):
        result = boxen("Test", {"margin": {"top": 2, "left": 3}})
        self._print_box("Margins Test", result)
        lines = result.split("\n")
        self.assertEqual(lines[0], "")
        self.assertEqual(lines[1], "")
        self.assertTrue(lines[2].startswith("   ┌"))

    def test_text_alignment(self):
        # Center alignment
        result = boxen("Test", {"textAlignment": "center", "width": 10})
        self._print_box("Center Alignment", result)
        lines = result.split("\n")
        self.assertIn("  Test  ", lines[1])

        # Right alignment
        result = boxen("Test", {"textAlignment": "right", "width": 10})
        self._print_box("Right Alignment", result)
        lines = result.split("\n")
        self.assertIn("    Test", lines[1])

    def test_colors(self):
        # Border color
        result = boxen("Test", {"borderColor": "red"})
        self._print_box("Red Border", result)
        self.assertIn("\x1b[31m", result)

        # Background color
        result = boxen("Test", {"backgroundColor": "green"})
        self._print_box("Green Background", result)
        self.assertIn("\x1b[42m", result)

        # Hex colors
        result = boxen("Test", {"borderColor": "#ff0000"})
        self._print_box("Hex Color Border", result)
        self.assertIn("38;2;255;0;0", result)

    def test_titles(self):
        # Left-aligned title
        result = boxen("Content", {"title": "Title", "borderStyle": "single"})
        self._print_box("Left-aligned Title", result)
        self.assertIn("┌ Title ┐", result)

        # Right-aligned title
        result = boxen(
            "Content", {"title": "Title", "titleAlignment": "right", "width": 10}
        )
        self._print_box("Right-aligned Title", result)
        top_line = result.split("\n")[0]
        self.assertTrue(top_line.endswith("Title ┐"))

    def test_fullscreen(self):
        result = boxen("Test", {"fullscreen": True})
        self._print_box("Fullscreen Test", result)
        lines = result.split("\n")
        first_line = lines[0]
        self.assertEqual(len(first_line), shutil.get_terminal_size().columns)

    def test_error_handling(self):
        with self.assertRaises(ValueError):
            boxen("Test", {"borderColor": "invalid"})

        with self.assertRaises(ValueError):
            boxen("Test", {"borderStyle": {"invalid": "border"}})

    def test_dim_border(self):
        result = boxen("Test", {"dimBorder": True})
        self._print_box("Dimmed Border", result)
        self.assertIn("\x1b[2m", result)

    def test_ansi_handling(self):
        colored_text = "\x1b[31mRedText\x1b[0m"
        result = boxen(colored_text, {"width": 20})
        self._print_box("ANSI Handling", result)

        # Match ANSI codes and text while ignoring alignment spaces
        pattern = r"\x1b\[31m.*RedText.*\x1b\[0m"
        self.assertRegex(result, pattern)

    def test_wrapping(self):
        long_text = (
            "This is a very long text that should wrap multiple times in the box"
        )
        result = boxen(long_text, {"width": 20})
        self._print_box("Text Wrapping", result)
        lines = result.split("\n")
        self.assertGreater(len(lines), 4)

    def test_height_control(self):
        result = boxen("Short", {"height": 5})
        self._print_box("Height Control", result)
        lines = result.split("\n")
        self.assertEqual(len(lines), 5)


if __name__ == "__main__":
    unittest.main()

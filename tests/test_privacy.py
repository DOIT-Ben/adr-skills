"""Exercise privacy screening without exposing detected values."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_privacy  # noqa: E402


class PrivacyAuditTest(unittest.TestCase):
    def test_classifies_synthetic_secrets_and_paths(self):
        token = "gh" + "p_" + "a" * 36
        personal_path = "C:" + "\\" + "Users" + "\\" + "sample-person" + "\\" + "notes.txt"
        findings = audit_privacy.scan_content((token + "\n" + personal_path).encode())
        self.assertTrue({"github_token", "windows_profile_path", "absolute_windows_path_requires_review"} <= findings)
        self.assertNotIn(token, " ".join(findings))

    def test_removed_secret_is_still_detected_in_history(self):
        with tempfile.TemporaryDirectory(prefix=".adr-skills-test-", dir=ROOT) as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            def commit(message):
                email = "123+test" + "@" + "users.noreply.github.com"
                subprocess.run(["git", "-C", str(root), "add", "--", "example.txt"], check=True)
                subprocess.run(["git", "-C", str(root), "-c", "user.name=Test", "-c", f"user.email={email}",
                                "commit", "-q", "-m", message], check=True)
            path = root / "example.txt"
            path.write_text("gh" + "p_" + "a" * 36, encoding="utf-8")
            commit("first")
            path.write_text("safe example", encoding="utf-8")
            commit("second")
            findings = audit_privacy.audit(root)
            self.assertIn(("history", "example.txt", "github_token"), findings)
            self.assertNotIn(("working-tree", "example.txt", "github_token"), findings)


if __name__ == "__main__":
    unittest.main()

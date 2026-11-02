import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_layout.py'
spec = importlib.util.spec_from_file_location('audit_layout', SCRIPT)
audit_layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_layout)


class AuditLayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, source):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding='utf-8')
        return target

    def test_cross_platform_rules_and_good_flutter_size(self):
        self.put('Layout.swift', 'let size = UIScreen.main.bounds\n.frame(width: 390)\n.ignoresSafeArea()\n')
        self.put('Layout.m', 'CGRect bounds = [UIScreen mainScreen].bounds;\n')
        self.put('Layout.tsx', 'const screen = Dimensions.get("screen");\nconst {width} = Dimensions.get("window");\n')
        self.put('Layout.dart', 'final size = MediaQuery.of(context).size;\nfinal fit = BoxFit.cover;\n')
        self.put('Layout.css', 'img {object-fit: cover;}\narticle {width: 390px;}\n')
        result = audit_layout.audit(self.root)
        names = {item['rule'] for item in result['findings']}
        self.assertTrue({'main-screen', 'fixed-dimension', 'safe-area-bypass', 'rn-screen-size', 'rn-window-snapshot', 'media-fill'} <= names)
        self.assertFalse(any(item['path'] == 'Layout.dart' and item['line'] == 1 for item in result['findings']))
        self.assertEqual(result['files_scanned'], 5)

    def test_skip_dependencies_secrets_hidden_files_and_symlinks(self):
        for name in ('node_modules/a.ts', '.hidden/a.swift', 'Pods/a.swift', 'DerivedData/a.swift', 'build/a.dart', 'vendor/a.css', '.env.swift', 'secrets.swift', 'credentials.ts'):
            self.put(name, 'UIScreen.main.bounds\n')
        external = self.root / 'outside'
        external.mkdir()
        secret = external / 'source.swift'
        secret.write_text('UIScreen.main.bounds\n', encoding='utf-8')
        project = self.root / 'project'
        project.mkdir()
        (project / 'source.swift').symlink_to(secret)
        (project / 'linked-dir').symlink_to(external, target_is_directory=True)
        result = audit_layout.audit(project)
        self.assertEqual(result['files_scanned'], 0)
        self.assertEqual(result['total_candidates'], 0)
        # All directories above are skipped when traversing the main fixture.
        external.rename(self.root / '.outside')
        result = audit_layout.audit(self.root)
        self.assertEqual(result['files_scanned'], 0)
        self.assertEqual(result['total_candidates'], 0)

    def test_truncation_counts_all_candidates_and_keeps_order(self):
        self.put('z.swift', 'UIScreen.main.bounds\nUIScreen.main.bounds\n')
        self.put('a.swift', 'UIScreen.main.bounds\n')
        result = audit_layout.audit(self.root, max_findings=1)
        self.assertEqual(result['total_candidates'], 3)
        self.assertEqual(len(result['findings']), 1)
        self.assertEqual(result['findings'][0]['path'], 'a.swift')
        self.assertTrue(result['truncated'])

    def test_cli_status_json_invalid_argument_and_source_unchanged(self):
        source = self.put('Layout.swift', 'UIScreen.main.bounds\n')
        before = source.read_bytes()
        run = subprocess.run(['python3', str(SCRIPT), str(self.root), '--format', 'json'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(json.loads(run.stdout)['total_candidates'], 1)
        self.assertEqual(source.read_bytes(), before)
        for args in ([str(self.root), '--max-findings', '0'], [str(self.root / 'missing')]):
            bad = subprocess.run(['python3', str(SCRIPT)] + args, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
        (self.root / 'linked').symlink_to(source)
        bad = subprocess.run(['python3', str(SCRIPT), str(self.root / 'linked')], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)

    def test_unreadable_encoding_and_large_file_are_reported(self):
        (self.root / 'binary.swift').write_bytes(b'\xff\xfe\x00')
        self.put('big.swift', 'x' * (audit_layout.MAX_FILE_BYTES + 1))
        result = audit_layout.audit(self.root)
        self.assertEqual(result['files_scanned'], 0)
        self.assertEqual(result['files_skipped'], 1)
        self.assertEqual(result['read_errors'][0]['error'], 'UnicodeDecodeError')


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for AppDocU Preprocessor & Normalizer
"""
import unittest
import tempfile
import os
from pathlib import Path
import json
from appdocu_preprocessor.normalize import DocumentNormalizer


class TestDocumentNormalizer(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.normalizer = DocumentNormalizer(str(self.test_dir))
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_calculate_file_hash(self):
        """Test file hash calculation for idempotency"""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Hello World", encoding='utf-8')
        
        hash1 = self.normalizer.calculate_file_hash(test_file)
        hash2 = self.normalizer.calculate_file_hash(test_file)
        
        self.assertEqual(hash1, hash2)
        
    def test_should_skip_directory(self):
        """Test directory skipping logic"""
        # Test hidden directory
        hidden_dir = self.test_dir / ".git"
        hidden_dir.mkdir()
        self.assertTrue(self.normalizer.should_skip_directory(hidden_dir))
        
        # Test documentation directory
        doc_dir = self.test_dir / "documentation"
        doc_dir.mkdir()
        self.assertTrue(self.normalizer.should_skip_directory(doc_dir))
        
        # Test node_modules directory
        node_dir = self.test_dir / "node_modules"
        node_dir.mkdir()
        self.assertTrue(self.normalizer.should_skip_directory(node_dir))
        
        # Test _normalized directory (this may already exist due to logging setup)
        norm_dir = self.test_dir / "_normalized"
        norm_dir.mkdir(exist_ok=True)  # Use exist_ok=True to handle if it already exists
        self.assertTrue(self.normalizer.should_skip_directory(norm_dir))
        
        # Test regular directory
        regular_dir = self.test_dir / "src"
        regular_dir.mkdir()
        self.assertFalse(self.normalizer.should_skip_directory(regular_dir))
        
    def test_write_index_files(self):
        """Test index and map file writing"""
        # Set up some test results
        self.normalizer.conversion_results = [
            {
                'source': 'docs/test.docx',
                'output': '_normalized/docx/test.md',
                'converter': 'docx_to_md',
                'status': 'success',
                'hash': 'test_hash_123'
            }
        ]
        self.normalizer.conversion_map = {
            'test.docx': '_normalized/docx/test.md'
        }
        
        # Write index files
        self.normalizer.write_index_files()
        
        # Verify files exist
        index_file = self.test_dir / "_normalized" / "normalize.index.json"
        map_file = self.test_dir / "_normalized" / "normalized-map.json"
        
        self.assertTrue(index_file.exists())
        self.assertTrue(map_file.exists())
        
        # Verify content
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        


        # Validate index_data structure
        self.assertIn('documents', index_data)
        self.assertIsInstance(index_data['documents'], list)
        self.assertGreater(len(index_data['documents']), 0)
        self.assertIn('source', index_data['documents'][0])
        self.assertIn('status', index_data['documents'][0])
        self.assertEqual(index_data['documents'][0]['source'], 'docs/test.docx')
        self.assertEqual(index_data['documents'][0]['status'], 'success')

        with open(map_file, 'r', encoding='utf-8') as f:
            map_data = json.load(f)
            # Validate map_data structure
            self.assertIn('test.docx', map_data)
            self.assertEqual(map_data['test.docx'], '_normalized/docx/test.md')


if __name__ == '__main__':
    unittest.main()

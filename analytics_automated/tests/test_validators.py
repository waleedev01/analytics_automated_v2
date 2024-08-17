import os
from analytics_automated.validators import *

from django.test import TestCase


class TaskValidators(TestCase):

    def setUp(self):
        self.test_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'submissions', 'files')

    def testAcceptPng(self):
        filepath = os.path.join(self.test_files_dir, 'test.png')
        f = open(filepath, "rb").read()
        self.assertTrue(png(f))

    def testRejectNonpng(self):
        filepath = os.path.join(self.test_files_dir, 'test.gif')
        f = open(filepath, "rb").read()
        self.assertFalse(png(f))

    def testAcceptGif(self):
        filepath = os.path.join(self.test_files_dir, 'test.gif')
        f = open(filepath, "rb").read()
        self.assertTrue(gif(f))

    def testRejectNonGif(self):
        filepath = os.path.join(self.test_files_dir, 'test.png')
        f = open(filepath, "rb").read()
        self.assertFalse(gif(f))

    def testAcceptJpeg(self):
        filepath = os.path.join(self.test_files_dir, 'test.jpeg')
        f = open(filepath, "rb").read()
        self.assertTrue(jpeg(f))

    def testRejectNonJpeg(self):
        filepath = os.path.join(self.test_files_dir, 'test.gif')
        f = open(filepath, "rb").read()
        self.assertFalse(jpeg(f))

    def testAcceptValidPDB(self):
        filepath = os.path.join(self.test_files_dir, '1iar.pdb')
        f = open(filepath, "rb").read()
        self.assertTrue(pdb_file(f))

    def testRegjectInvalidPDB(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(pdb_file(f))

    def testAcceptFasta(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA.fasta')
        f = open(filepath, "rb").read()
        self.assertTrue(seq(f))

    def testRejectNoSeq(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA_noseq.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(seq(f))

    def testRejectEmpty(self):
        filepath = os.path.join(self.test_files_dir, 'empty.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(seq(f))

    def testRejectNucleotide(self):
        filepath = os.path.join(self.test_files_dir, 'nucleotide.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(seq(f))

    def testRejectBadSeq(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA_badseq.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(seq(f))

    def testAcceptMSA(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA_msa.fasta')
        f = open(filepath, "rb").read()
        self.assertTrue(seq(f))

    def testRejectBadMSA(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA_badmsa.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(seq(f))

    def testRejectBadHeaderMSA(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA_badmultipleheader.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(seq(f))

    def testRejectMSAWithBadChar(self):
        filepath = os.path.join(self.test_files_dir, '5ptpA_badcharmsa.fasta')
        f = open(filepath, "rb").read()
        self.assertFalse(seq(f))

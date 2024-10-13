"""Sample splint module with check functions"""
from splint import rule_files
from src import splint


@splint.attributes(tag="folder", ruid="f1", level=1, phase="proto")
def check_folder1():
    """ Simple always passing function"""
    yield from rule_files.rule_path_exists('../examples/file_system/folder1')


@splint.attributes(tag="folder", ruid="f2", level=1, phase="proto")
def check_folder2():
    """ Simple always passing function"""
    yield from rule_files.rule_path_exists('../examples/file_system/folder2')


@splint.attributes(tag="folder", ruid="file2", level=1, phase="proto")
def check_files_f2():
    """ Simple always passing function"""
    for f in ['file1.txt', 'file2.txt']:
        yield from rule_files.rule_path_exists(f'../examples/file_system/folder2/{f}')


@splint.attributes(tag="folder", ruid="file1", level=1, phase="proto")
def check_files_f1():
    """ Simple always passing function"""
    for f in ['file1.txt', 'file2.txt']:
        yield from rule_files.rule_path_exists(f'../examples/file_system/folder1/{f}')

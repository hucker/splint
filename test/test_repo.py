import src.splint as splint


def test_splint_repo():
    repo = splint.SplintRepo(pkg_folder='./test/repo',pkg_glob='check_pkg_*')
    results = repo.run_pkgs()
    assert len(results) == 4
    expected_functions = ['check_pkg_1_1','check_pkg_1_2','check_pkg_2_1','check_pkg_2_2']              # there should be 4 results
    assert sum(r.status for r in results ) == 4  # all 4 checks should pass
    assert all(r.function_name in expected_functions for r in results) # all 4 checks should be in the list of expected functions
    assert sum(r.tag == 'Pkg1' for r in results) == 2
    assert sum(r.tag == 'Pkg2' for r in results) == 2
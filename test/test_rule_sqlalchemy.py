import pytest
from sqlalchemy import MetaData, Table, Column, String, Integer, create_engine
from src import splint


@pytest.fixture
def engine():
    
    engine = create_engine('sqlite:///:memory:')
    metadata = MetaData()
    metadata.bind = engine

    # Define a table
    table = Table(
        'users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('email', String),
        Column('age', Integer)
    )

    # Drop the table if it exists
    table.drop(engine, checkfirst=True)

    # Create all tables in the metadata
    metadata.create_all(engine)

    yield engine


@pytest.mark.parametrize(
    "expected_columns, expected_results",
    [
        (
                ['id', 'name', 'email', 'age'],
                [
                    splint.SplintResult(status=True, msg="Column 'id' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'name' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'email' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'age' is correctly present in table users")
                ]
        ),
        (
                ['id', 'name', 'email', 'age', 'unexpected'],
                [
                    splint.SplintResult(status=True, msg="Column 'id' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'name' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'email' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'age' is correctly present in table users"),
                    splint.SplintResult(status=False, msg="Missing column in table users: unexpected")
                ]
        ),
    ],
)
def test_rule_sql_table_schema(engine, expected_columns, expected_results):
    # Call the function with the expected columns list
    results = list(splint.rule_sql_table_schema(engine, 'users', expected_columns))

    # NOTE: This is a bit tricky, you would think you could just compare the lists, but the code that runs
    #       runs the rule fills in other low level details that we aren't concenred with
    bools = list( r.msg == e.msg and r.status==e.status for e,r in zip(results,expected_results))
    assert all( bools)



@pytest.mark.parametrize(
    "expected_columns, expected_results",
    [
        (
                ['name', 'email', 'age'],
                [
                    splint.SplintResult(status=True, msg="Column 'name' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'email' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'age' is correctly present in table users")
                ]
        ),
        (
                ['id', 'name', 'email'],
                [
                    splint.SplintResult(status=True, msg="Column 'id' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'name' is correctly present in table users"),
                    splint.SplintResult(status=True, msg="Column 'email' is correctly present in table users"),
                ]
        ),
    ],
)
def test_rule_sql_table_schema_with_extra(engine, expected_columns, expected_results):
    # Call the function with the expected columns list
    results = list(splint.rule_sql_table_schema(engine, 'users', expected_columns,extra_columns_ok=True))

    # NOTE: This is a bit tricky, you would think you could just compare the lists, but the code that 
    #       runs the rule fills in other low level details that we aren't concerned with
    #assert all(r.msg == e.msg and r.status == e.status for e, r in zip(results, expected_results))
    assert all(r.status == e.status for e, r in zip(results, expected_results))


def test_rule_sql_table_bad_table(engine):
    # Call the function with the expected columns list
    results = list(splint.rule_sql_table_schema(engine, table='',expected_columns=['users'], extra_columns_ok=True))

    assert results[0].msg == "Table name cannot be blank."
    assert not results[0].status

def test_rule_sql_table_bad_column(engine):
    # Call the function with the expected columns list
    results = list(splint.rule_sql_table_schema(engine, table='users',expected_columns=[''], extra_columns_ok=True))

    assert results[0].msg == "Column names cannot be empty."    
    assert not results[0].status
    
def test_rule_sql_table_bad_column_list(engine):
    # Call the function with the expected columns list
    results = list(splint.rule_sql_table_schema(engine, table='users',expected_columns=[], extra_columns_ok=True))

    assert not results[0].status
    assert results[0].msg == "Column list cannot be empty."
    
def test_rule_sql_table_bad_extra_columns(engine):
    # Call the function with the expected columns list
    results = list(splint.rule_sql_table_schema(engine, table='users',expected_columns=['id','name'], extra_columns_ok=False))
    msgs = ["Column 'id' is correctly present in table users"  ,
            "Column 'name' is correctly present in table users",
            "Unexpected column in table users: email",
            "Unexpected column in table users: age",
            ]
    
    # This is very screwy, but I've had issues with different versions of python returning the results
    # in slightly different orders.  So first I'm verifying that I get 4 different messages back and
    # then I check that each message is in the result set.⁄
    # This is not ideal and should be refactored
    assert len(set([result.msg for result in results])) == 4
           
    for result in results:
        assert (result.status is False) if "Unexpected" in result.msg else (result.status is True)  
        assert result.msg in msgs

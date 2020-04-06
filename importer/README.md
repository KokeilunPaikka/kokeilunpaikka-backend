This is a temporary tool for migrating data from the current production to the new (production) environment. This package may be removed later when it has become unnecessary.

The migration process consists of:
1. Running predefined SQL queries from SQL client like HeidiSQL
2. Exporting query results as CSV
3. Importing CSV data using django command provided by this package

Import command should be run in the following order because of the relations of the datasets:
1. themes
2. users
3. experiments
4. experiment_data

SQL queries for the migration can be found on internal network drive as well as a screenshot of CSV export settings used with HeidiSQL. The export may well be run using the official MySQL CLI as well while using the similar settings.
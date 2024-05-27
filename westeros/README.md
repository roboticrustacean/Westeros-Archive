Usage
Input File: The input file should contain commands for creating types, records, deleting records, and searching records.
Running the Script: Execute the script with the input file path as an argument:

python3 2020400255/archive.py input_file_path
Output and Log Files: The script generates output.txt for search results and log.csv for logging all operations.

Sample input.txt file:

create type human 6 1 name str origin str title str age int weapon str skill str
create record human RamsayBolton Dreadfort Lord 21 Dagger Strategy
create type dragon 5 1 name str age int color str owner str skill str
create record dragon Viserion 5 White NightKing IceBreathing
create record human Bronn Stokeworth Knight 32 Crossbow Swordfighting
delete record human NedStark
search record human RamsayBolton
search record dragon Viserion
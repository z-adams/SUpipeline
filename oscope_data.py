import numpy as np
import re

def separate_line_csv(line):
    """Splits the lines based on a sequence of delimiters
    Separates by commas (,\ *), newlines (\r\n),
    a series of >= 2 spaces (\ {2,}), or a sequence consisting of a colon
    followed by at least 1 space and optionally terminated by a comma (:\ +,*)

    args:
    line -- a string to split using the aforementioned delimiters

    returns a list containint the chunks of split string
    """
    split_line = re.split(r':\ +,*|\ {2,}|,\ *|\r\n', line)
    return [elem for elem in split_line if elem != '']

def parse_raw_columns(filename):
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            lines.append(line)

    col_data = []
    first_line = separate_line_csv(lines[0])
    n_cols = len(first_line)
    for c in range(n_cols):
        col_data.append([])

    for line in lines:
        split_line = separate_line_csv(line)
        for c in range(n_cols):
            col_data[c].append(split_line[c])
    output = []
    for col in col_data:
        output.append(np.array(col))
    return output

def parse_oscope(filename):
    """Parse a csv file from the Agilent Infiniium scope
    Assumes that columns will have column titles (assert will fail if not),
    I've seen different formats.

    args:
    filename -- the path of the file to parse

    returns a file_data dict containing the header elements as keys, as well
    as a 'data' list containing the data columns and titles.

    """

    # parse file into list of lines
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            lines.append(line)

    # Used to decide what datatype to parse header values into
    int_elements = ['Revision', 'Start', 'Points', 'Count', 'Max Bandwidth',
            'Min Bandwidth']
    float_elements = ['XDispRange', 'XDispOrg', 'XInc', 'XOrg',
            'YDispRange', 'YDispOrg', 'YInc', 'YOrg']
    
    # parse header information
    i = 0
    header_parsed = False
    file_data = {}
    while not header_parsed:
        split_line = separate_line_csv(lines[i])

        # Check for existence of a leading title line (e.g. "Channel 2")
        # Temporarily currently just skip it
        if i == 0:
            #if len(split_line) == 1:
                #file_data['title'] = split_line[0]
                i += 1
                continue
        
        # Check to see if we've hit the end of the header data
        if split_line[0] == 'Min Bandwidth':
            header_parsed = True

        # Parse each header line into dict elements
        if split_line[0] in int_elements:
            file_data[split_line[0]] = int(split_line[1])
        elif split_line[0] in float_elements:
            file_data[split_line[0]] = float(split_line[1])
        else:
            file_data[split_line[0]] = split_line[1]
        i += 1

    # Find column titles
    column_titles = separate_line_csv(lines[i])
    i += 1

    columns = []
    # Create n empty arrays to store the columns of data
    # Split the first row of data but don't advance i
    # (need to split again to capture the values)
    first_row = separate_line_csv(lines[i])
    for c in range(len(first_row)):
        columns.append([])

    # For the rest of the lines in the file...
    while i < len(lines):
        split_line = separate_line_csv(lines[i])

        # ...make sure that the number of columns matches the expected value...
        assert len(split_line) == len(first_row)

        # ...and insert the values into their respective column lists
        for c in range(len(first_row)):
            columns[c].append(float(split_line[c]))

        i += 1

    # Create a 'data' element of the file dict and insert data arrays
    # data columns are stored in a tuple with structure ('title', np.array)
    file_data['data'] = []
    for c in range(len(first_row)):
        file_data['data'].append( (column_titles[c], np.array(columns[c]),) )

    return file_data

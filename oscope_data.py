import re

def separate_line_csv(line):
    """Splits the lines based on a sequence of delimiters
    Separates by commas (,\ *), a series of >= 2 spaces (\ {2,}),
    or a sequence consisting of a colon followed by at least 1 space and
    optionally terminated by a comma (:\ +,*)

    args:
    line -- a string to split using the aforementioned delimiters

    returns a list containint the chunks of split string
    """
    return re.split(r'((:\ +,*)|(\ {2,})|(,\ *))', line)

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
        if i == 0:
            if len(split_line) == 1:
                file_data['title'] = split_line[0]
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
    for c in range(len(column_titles)):
        columns.append([])

    # For the rest of the lines in the file...
    while i < len(lines):
        split_line = separate_line_csv(lines[i])

        # ...make sure that the number of columns matches the expected value...
        assert len(split_line) == len(column_titles)

        # ...and insert the values into their respective column lists
        for c in range(len(column_titles)):
            columns[c].append(float(split_line[c]))

        i += 1

    # Create a 'data' element of the file dict and insert data arrays
    # data columns are stored in a tuple with structure ('title', np.array)
    file_data['data'] = []
    for c in range(len(column_titles)):
        file_data['data'].append( (column_titles[i], np.array(columns[i]),) )

    return file_data

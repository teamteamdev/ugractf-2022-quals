current_output = None

with open("base.sfd", "r") as source:
    for line in source:
        if line.startswith("Encoding:") and "UnicodeBmp" not in line:
            char_id = line.split()[1]

            current_output = open(f"characters/{char_id}", "w")
        elif line == "EndChar\n":
            current_output.close()
            current_output = None
        elif current_output is not None:
            current_output.write(line)

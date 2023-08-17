"""
    2023.8.17
    ref: https://biobank.ndph.ox.ac.uk/showcase/label.cgi?id=100118
    
"""

import os

def load_table():
    fname = "Field_ID.txt"
    field_table = []
    with open(fname, "r") as f:
        lines = f.readlines()
        for l in lines[1:]:
            row = l.split("\t")
            row[1] = row[1].strip()
            row.append(row[1].replace(" ", "_"))
            for s in "\\(),-/":
                row[2] = row[2].replace(s, "")
            if len(row[2]) > 10:
                row[2] = row[2][:5] + "_" + row[2][-5:]
            while True:
                row[2] = row[2].replace("__", "_")
                if not "__" in row[2]:
                    break

            field_table.append(row)
            # print(row[2])

    return field_table


# 把多行语句放到一行
def format_multi_line_str(str_list, step=5, pref="\t"):
    ret_list = []
    for i in range(0, len(str_list), step):
        ret_list.append(pref + " ".join(str_list[i:i+step]))

    return ret_list


def gen_code_all_field(str_format, field_table):
    str_tmp = []
    for field in field_table:
        str_tmp.append(str_format.format(fid=field[0], fname=field[1], fdetail=field[2]))
    return format_multi_line_str(str_tmp)


def gen_code(field_table):
    str = []
    # write field table
    str.append(f"/* feild_id_table */")
    str.append("/* Reference: https://biobank.ndph.ox.ac.uk/showcase/label.cgi?id=100118 */")
    str.append("/*")
    for field in field_table:
        str.append(f" {field[0]}\t{field[2]}\t{field[1]}")
    str.append("*/")

    str.append("\n")

    # write all vars
    str.append("/* All Vars */")
    str.append("/*")
    str_tmp = []
    for field in field_table:
        for i in range(5):
            str_tmp.append(f"n_{field[0]}_{i}_0")
    str = str + format_multi_line_str(str_tmp, step=5)
    str.append("*/")

    # calculate_mean
    str.append("/* calculate_mean */")
    str_tmp = []
    for field in field_table:
        str_tmp.append(f"mean_{field[0]} = mean(of n_{field[0]}_0_0-n_{field[0]}_4_0);")
    str = str + format_multi_line_str(str_tmp)
    # Can also write as:
    #   str = str + gen_code_all_field("mean_{fid} = mean(of n_{fid}_0_0-n_{fid}_4_0);", field_table)

    # calculate_n
    str.append("/* calculate_n */")
    str_tmp = []
    for field in field_table:
        str_tmp.append(f"n_of_{field[0]} = n(of n_{field[0]}_0_0-n_{field[0]}_4_0);")
    str = str + format_multi_line_str(str_tmp)

    # get_miss_var
    str.append("/* get_miss_var */")
    str_tmp = []
    for field in field_table:
        str_tmp.append(f"if n_of_{field[0]} = 1 then mean_{field[0]} = .;")
    str = str + format_multi_line_str(str_tmp)

    # rename variable
    str.append("/* rename variable */")
    str.append("rename")
    str_tmp = []
    for field in field_table:
        str_tmp.append(f"mean_{field[0]}={field[2]}")
    str = str + format_multi_line_str(str_tmp)
    print(str_tmp)

    return str
    

if __name__ == "__main__":
    field_table = load_table()
    # print(field_table)
    code_str = gen_code(field_table)

    with open("gen_code.sas", "w") as f:
        f.write("\n".join(code_str))
    
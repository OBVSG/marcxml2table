import sys
import re
import xml.etree.ElementTree as ET
from collections import Counter
from rich.pretty import pprint

xml_iterator = ET.iterparse(sys.argv[1])
output_file = sys.argv[2]
filter_ = sys.argv[3].split()


def parse_record(fields, record):
    record_dict = {}
    for field in fields:
        if field == "leader":
            leader = record.find("./leader")
            res = ""
            if leader is not None:
                res = leader.text
            record_dict["000leader"] = res

        if field[0:2] == "00" and int(field[2]) <= 9:
            controlfield = record.find(f"./controlfield[@tag='{field}']")
            res = ""
            if controlfield is not None:
                res = controlfield.text
            record_dict[field] = res

        else:
            datafields = record.findall(f"./datafield[@tag='{field}']")

            for i, datafield in enumerate(datafields, start=1):
                field_name = "".join(
                    (
                        datafield.attrib.get("tag"),
                        datafield.attrib.get("ind1").replace(" ", "#"),
                        datafield.attrib.get("ind2").replace(" ", "#"),
                        f" ({i})",
                    )
                )
                subfield_distribution = Counter([i.attrib.get("code") for i in datafield])
                uniques = [k for k, v in subfield_distribution.items() if v == 1]
                multiple = [k for k, v in subfield_distribution.items() if v > 1]

                print(subfield_distribution, uniques, multiple)

                for sf_code in uniques:
                    sf = datafield.find(f"./subfield[@code='{sf_code}']")
                    record_dict["".join((field_name, " ", sf_code, "No:0"))] = sf.text

                for sf_code in multiple:
                    for i, occurence in enumerate(datafield.findall(f"./subfield[@code='{sf_code}']")):
                        record_dict["".join((field_name, " ", sf_code, f"No:{i}"))] = occurence.text
    return record_dict


list_of_dics = list()
for _, element in xml_iterator:
    if element.tag == "record":
        list_of_dics.append(parse_record(filter_, element))

header = sorted(list(set((k for dic in list_of_dics for k in dic))))
header_formatted = "\t".join([re.sub(r"No:\d+", "", i) for i in header]).replace("000leader", "leader")


with open(output_file, "w", encoding="utf-8") as f:
    f.write(header_formatted)
    f.write("\n")
    for dic in list_of_dics:
        row_list = list()
        for col in header:
            if dic.get(col):
                row_list.append(dic.get(col))
            else:
                row_list.append("")
        f.write("\t".join(row_list))
        f.write("\n")



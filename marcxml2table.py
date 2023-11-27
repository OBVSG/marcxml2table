import re
import csv
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path


parser = ArgumentParser(
    description="Convert Marc XML to tsv table where every subfield is a separate column."
)
parser.add_argument(
    "input_xml", type=Path, help="File containing the MARCXML Data. No namespaces!"
)
parser.add_argument(
    "output_tsv", type=Path, help="File to write the tab separated file to."
)
parser.add_argument(
    "filter",
    type=str,
    help="Blank-separated list of fields to be exported; 'leader 001 245 85640 912'. To filter fields with specific indicators, use a 5-digit marc field. Use a # sign for blank and a * sign as wildcard for any indicator.",
)
args = parser.parse_args()


def sort_key(field: str) -> tuple:
    field_splitted = field.split()
    field_number = field_splitted[0]
    field_occurence = int(field_splitted[1].replace("[", "").replace("]", ""))
    subfield_code = field_splitted[2].split("No:")[0]
    subfield_occurence = int(field_splitted[2].split("No:")[1])
    return (field_number, field_occurence, subfield_code, subfield_occurence)


def parse_record(fields: list, record: ET.Element) -> dict:
    record_dict = {}
    for field in fields:
        if field == "leader":
            leader = record.find("./leader")
            res = ""
            if leader is not None:
                res = leader.text
            record_dict["000 [1] CFNo:0"] = res

        if field[0:2] == "00" and int(field[2]) <= 9:
            controlfield = record.find(f"./controlfield[@tag='{field}']")
            res = ""
            if controlfield is not None:
                res = controlfield.text
            record_dict[" ".join((field, "[1] CFNo:0"))] = res

        else:
            xpath = f"./datafield[@tag='{field[:3]}']"
            if len(field) == 5:
                field = field.replace("#", " ")
                if field[3] != "*":
                    xpath = xpath + f"[@ind1='{field[3]}']"
                if field[4] != "*":
                    xpath = xpath + f"[@ind2='{field[4]}']"
            datafields = record.findall(xpath)
            for i, datafield in enumerate(datafields, start=1):
                field_name = "".join(
                    (
                        datafield.attrib.get("tag"),
                        datafield.attrib.get("ind1").replace(" ", "#"),
                        datafield.attrib.get("ind2").replace(" ", "#"),
                        f" [{i}]",
                    )
                )
                subfield_distribution = Counter(
                    [i.attrib.get("code") for i in datafield]
                )
                uniques = [k for k, v in subfield_distribution.items() if v == 1]
                multiple = [k for k, v in subfield_distribution.items() if v > 1]

                for sf_code in uniques:
                    sf = datafield.find(f"./subfield[@code='{sf_code}']")
                    record_dict["".join((field_name, " ", sf_code, "No:0"))] = sf.text

                for sf_code in multiple:
                    for i, occurence in enumerate(
                        datafield.findall(f"./subfield[@code='{sf_code}']")
                    ):
                        record_dict[
                            "".join((field_name, " ", sf_code, f"No:{i}"))
                        ] = occurence.text
    return record_dict


list_of_dics = list()
for _, element in ET.iterparse(args.input_xml):
    if element.tag == "record":
        list_of_dics.append(parse_record(args.filter.split(), element))


header = list(set((k for dic in list_of_dics for k in dic)))
sorted_header = sorted(header, key=sort_key)
header_formatted = list()
for field in sorted_header:
    if field.startswith("000"):
        field = field.replace("000", "leader", 1)
    if "CFNo:" in field:
        header_formatted.append(field.split()[0])
    else:
        header_formatted.append(re.sub(r"No:\d+$", "", field))


with open(args.output_tsv, "w", encoding="utf-8", newline="") as csvfile:
    csvfile.write("\t".join(header_formatted) + "\r\n")
    writer = csv.DictWriter(
        csvfile,
        fieldnames=sorted_header,
        quoting=csv.QUOTE_ALL,
        delimiter="\t",
        quotechar="'",
    )
    for dic in list_of_dics:
        writer.writerow(dic)

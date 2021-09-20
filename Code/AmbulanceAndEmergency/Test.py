import CSV_Parser

if __name__ == '__main__':
    # Emergency_path =  r"C:/Users/predator/Desktop/PSCR/projects/Parser/CSV_Files/AmbulanceAndEmergency.xlsx"
    Emergency_path = r"C:/Users/predator/Desktop/PSCR/projects/Parser/CSV_Files/CSVNumberOfStaffAndVolunteersSheet1.xlsx"

    # CSV_Parser.CSV_Parser(Emergency_path,"عدد المنتفعين" )
    # CSV_Parser.CSV_Parser(Emergency_path,"عدد العاملين والمتطوعين")
    # CSV_Parser.CSV_Parser(Emergency_path,"عدد العاملين والمتطوعين")
    res = CSV_Parser.CSV_Parser(Emergency_path, "عدد العاملين والمتطوعين")
    res.display()

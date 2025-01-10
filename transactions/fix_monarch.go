// fix_monarch fixes dates and parent categories for Monarch transactions
package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"slices"
	"strings"
)

// Sheet contains a spreadsheet
type Sheet struct {
	fname string
	rows  [][]string
}

var (
	fnameFlag = flag.String("f", "/home/scottkirkwood/Downloads/monarch-transactions.csv", "Import Monarch filename")
        filterCategoriesFlag = flag.String("filter_categories", "Mortgage,Transfer,Paychecks", "Categories to remove, comma separated")
)

type Categories struct {
	db                    []string
	ParentCategories      map[string]bool
	SubCategoriesToParent map[string]string
}

var subCategories = []string{
	">Income",
	"Paychecks",
	"Interest",
	"Business Income",
	"Other Income",
	"Dividends & Capital Gains",
	">Expenses",
	"Gifts & Donations",
	"Charity",
	"Gifts",
	">Auto & Transport",
	"Auto Payment",
	"Public Transit",
	"Auto",
	"Auto Maintenance",
	"Parking & Tolls",
	"Taxi & Ride Shares",
	">Housing",
	"Mortgage",
	"Home Improvement",
	"Rent",
	">Bills & Utilities",
	"Garbage",
	"Water",
	"Gas & Electric",
	"Internet & Cable",
	"Phone",
	"Misc",
	">Food & Dining",
	"Groceries",
	"Restaurants & Bars",
	"Coffee Shops",
	"Alcohol",
	">Travel & Lifestyle",
	"Travel & Vacation",
	"Entertainment & Recreation",
	"Personal",
	"Pets",
	"Fun Money",
	"Hobbies",
	"Boat",
	">Shopping",
	"Shopping",
	"Clothing",
	"Furniture & Housewares",
	"Electronics",
	">Children",
	"Child Activities",
	"Child Care",
	"Create Category",
	"EducationEdit",
	"Student Loans",
	"Education",
	">Health & Wellness",
	"Medical",
	"Dentist",
	"Fitness",
	"Tennis",
	">Financial",
	"Loan Repayment",
	"Financial & Legal Services",
	"Financial Fees",
	"Cash & ATM",
	"Insurance",
	"Taxes",
	">Other",
	"Uncategorized",
	"Check",
	"Miscellaneous",
	">Business",
	"Advertising & Promotion",
	"Business Utilities & Communication",
	"Employee Wages & Contract Labor",
	"Business Travel & Meals",
	"Business Auto Expenses",
	"Business Insurance",
	"Office Supplies & Expenses",
	"Office Rent",
	"Postage & Shipping",
	">Transfers",
	"Transfer",
	"Credit Card Payment",
	"Balance Adjustments",
}

func importFile(fname string) (*Sheet, error) {
	f, err := os.Open(fname)
	if err != nil {
		return nil, fmt.Errorf("unable to read input file "+fname, err)
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	rows, err := csvReader.ReadAll()
	return &Sheet{
		fname: fname,
		rows:  rows,
	}, err
}

func (s *Sheet) writeFile(fname string) error {
	f, err := os.Create(fname)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	w.WriteAll(s.rows)
	return nil
}

// colIndex returns the 0 based index of the column or -1 if not found
func (s *Sheet) colIndex(colName string) int {
	return slices.Index(s.rows[0], colName)
}

// addSubCategories searches `colName` and adds `newColName`
// to the left which will be the parent category
func (s *Sheet) addSubCategories(colName, newColName string, subCategories Categories) error {
	colNameIndex := s.colIndex(colName)
	if colNameIndex < 0 {
		return fmt.Errorf("column %q not found", colName)
	}
	for i, row := range s.rows {
		s.rows[i] = slices.Insert(s.rows[i], colNameIndex, "")
		if i == 0 {
			s.rows[i][colNameIndex] = colName
			s.rows[i][colNameIndex+1] = newColName
			continue
		}
		category := row[colNameIndex]
		if category == "" {
			return fmt.Errorf("Missing category in line %d", i+1)
		}
		if subCategories.ParentCategories[category] {
			s.rows[i][colNameIndex] = category
			s.rows[i][colNameIndex+1] = ""
		} else {
			parent := subCategories.SubCategoriesToParent[category]
			if parent == "" {
				return fmt.Errorf("missing parent for category %q", category)
			}
			s.rows[i][colNameIndex] = parent
			s.rows[i][colNameIndex+1] = category
		}
	}
	return nil
}

// removeRows executes the function on the column passed and removes those rows
func (s *Sheet) removeRows(colName string, removeFn func(string)bool) error {
	colNameIndex := s.colIndex(colName)
	if colNameIndex < 0 {
		return fmt.Errorf("column %q not found", colName)
	}
	deleteFn := func(row []string) bool {
		return removeFn(row[colNameIndex])
	}
        s.rows = slices.DeleteFunc(s.rows, deleteFn)
	return nil
}

// dateToMonth searches for `colName` and adds `newColName` to the right
// after applying the function to the string
func (s *Sheet) mapToNewCol(colName, newColName string, mapFn func(string)string) error {
	colNameIndex := s.colIndex(colName)
	if colNameIndex < 0 {
		return fmt.Errorf("column %q not found", colName)
	}
	for i, row := range s.rows {
		// Inserts a blank column to right
		s.rows[i] = slices.Insert(s.rows[i], colNameIndex+1, "")
		if i == 0 {
			s.rows[i][colNameIndex+1] = newColName
			continue
		}
		val := row[colNameIndex]
		newVal := mapFn(val)
		s.rows[i][colNameIndex] = val
		s.rows[i][colNameIndex+1] = newVal
	}
	return nil
}

func mapDateToYYYYMM(txt string) string {
	if len(txt) < 8 {
		return txt
	}
	return txt[0:7]
}

func initCategories(subCategories []string) Categories {
	parents := map[string]bool{}
	children := map[string]string{}
	parent := ""
	for _, cat := range subCategories {
		if strings.HasPrefix(cat, ">") {
			parent = cat[1:]
			parents[parent] = true
		} else {
			children[cat] = parent
		}
	}
	return Categories{
		db:                    subCategories,
		ParentCategories:      parents,
		SubCategoriesToParent: children,
	}
}

func main() {
	flag.Parse()
	fmt.Printf("Importing %s\n", *fnameFlag)
	sheet, err := importFile(*fnameFlag)
	if err != nil {
		fmt.Printf("err %v\n", err)
		return
	}

	filterCategories := strings.Split(*filterCategoriesFlag, ",")
	removeRowFn := func (txt string) bool {
		return slices.Contains(filterCategories, txt)
	}
	if err := sheet.removeRows("Category", removeRowFn); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
	categories := initCategories(subCategories)
	if err := sheet.addSubCategories("Category", "Subcategory", categories); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
	if err := sheet.mapToNewCol("Date", "YYYYMM", mapDateToYYYYMM); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}

	fmt.Printf("%d rows\n", len(sheet.rows))
	outFile := strings.TrimSuffix(*fnameFlag, ".csv") + ".out.csv"
	fmt.Printf("Exporting %s\n", outFile)
	if err := sheet.writeFile(outFile); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
}

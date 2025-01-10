// fix_monarch fixes dates and parent categories for Monarch transactions
package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"slices"
	"strconv"
	"strings"
)

// Sheet contains a spreadsheet
type Sheet struct {
	fname string
	rows  [][]string
}

var (
	// fnameFlag = flag.String("f", "/home/scottkirkwood/Downloads/monarch-transactions.csv", "Import Monarch filename")
	fnameFlag            = flag.String("f", "/usr/local/google/home/scottkirkwood/Downloads/monarch-transactions.csv", "Import Monarch filename")
	removeFirstLastFlag  = flag.Bool("remove_first_last", true, "Remove first and last months as they may be incomplete")
	filterCategoriesFlag = flag.String("filter_categories", "Mortgage,Transfer,Transfers,Paychecks,Credit Card Payment", "Categories to remove, comma separated")
)

type Categories struct {
	db                    []string
	ParentCategories      map[string]bool
	SubCategoriesToParent map[string]string
}

const (
	yyyyMmColumn      = "YYYYMM"
	dateColumn        = "Date"
	categoryColumn    = "Category"
	subcategoryColumn = "Subcategory"
	amountColumn      = "Amount"
)

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
	"Education",
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

// getValue returns the 1's based row for column
// I.e. the row index of 1 is the first non-header row
func (s *Sheet) getValue(colName string, row int) string {
	colIndex := s.colIndex(colName)
	if colIndex < 0 {
		return fmt.Sprintf("bad col name %q", colName)
	}
	return s.rows[row][colIndex]
}

// addSubCategories searches `colName` and adds `newColName`
// to the left which will be the parent category
func (s *Sheet) addSubCategories(colName, newColName string, subCategories Categories) error {
	colNameIndex := s.colIndex(colName)
	newColIndex := colNameIndex + 1
	if colNameIndex < 0 {
		return fmt.Errorf("column %q not found", colName)
	}
	for i, row := range s.rows {
		s.rows[i] = slices.Insert(s.rows[i], colNameIndex+1, "")
		if i == 0 {
			s.rows[i][newColIndex] = newColName
			continue
		}
		category := row[colNameIndex]
		if category == "" {
			return fmt.Errorf("Missing category in line %d, %d, %#v", i+1, colNameIndex, row)
		}
		if subCategories.ParentCategories[category] {
			s.rows[i][colNameIndex] = category
			s.rows[i][newColIndex] = category
		} else {
			parent := subCategories.SubCategoriesToParent[category]
			if parent == "" {
				return fmt.Errorf("missing parent for category %q", category)
			}
			s.rows[i][colNameIndex] = parent
			s.rows[i][newColIndex] = category
		}
	}
	return nil
}

// removeRows executes the function on the column passed and removes those rows
func (s *Sheet) removeRows(colName string, removeFn func(string) bool) (int, error) {
	colNameIndex := s.colIndex(colName)
	if colNameIndex < 0 {
		return 0, fmt.Errorf("column %q not found", colName)
	}
	count := 0
	deleteFn := func(row []string) bool {
		toRemove := removeFn(row[colNameIndex])
		if toRemove {
			count++
		}
		return toRemove
	}
	s.rows = slices.DeleteFunc(s.rows, deleteFn)
	return count, nil
}

// removeFn executes the function on the column passed and removes those rows
func (s *Sheet) removeFn(removeFn func([]string) bool) (int, error) {
	count := 0
	deleteFn := func(row []string) bool {
		toRemove := removeFn(row)
		if toRemove {
			count++
		}
		return toRemove
	}
	s.rows = slices.DeleteFunc(s.rows, deleteFn)
	return count, nil
}

func (s *Sheet) removeIfFn(row []string) bool {
	subCategory := row[s.colIndex(subcategoryColumn)]
	amount, err := strconv.ParseFloat(row[s.colIndex(amountColumn)], 64)
	if err != nil {
		fmt.Printf("Unable to parse Amount %v\n", err)
		return false
	}

	if amount >= 0 {
		// Remove all income
		return true
	}
	if subCategory == "Auto" {
		// Remove large Auto payment
		return amount < -10000
	}
	if subCategory == "Boat" {
		// Remove large Boat payments
		return amount <= -3000
	}

	return false // keep row
}

// dateToMonth searches for `colName` and adds `newColName` to the right
// after applying the function to the string
func (s *Sheet) mapToNewCol(colName, newColName string, mapFn func(string) string) error {
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

func (s *Sheet) removeFirstAndLastMonths() error {
	startMonth := s.getValue(yyyyMmColumn, 1)
	lastMonth := s.getValue(yyyyMmColumn, len(s.rows)-1)
	count, err := s.removeRows(yyyyMmColumn, func(txt string) bool {
		return txt == startMonth || txt == lastMonth
	})
	fmt.Printf("Removed %d rows from start and end of list\n", count)
	return err
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
	filterCategories := strings.Split(*filterCategoriesFlag, ",")
	categories := initCategories(subCategories)

	fmt.Printf("Importing %s\n", *fnameFlag)
	sheet, err := importFile(*fnameFlag)
	if err != nil {
		fmt.Printf("err %v\n", err)
		return
	}

	if err := sheet.mapToNewCol(dateColumn, yyyyMmColumn, mapDateToYYYYMM); err != nil {
		fmt.Printf("mapToNewCol err %v\n", err)
		return
	}
	if *removeFirstLastFlag {
		if err := sheet.removeFirstAndLastMonths(); err != nil {
			fmt.Printf("removeFirstAndLastMonths err %v\n", err)
			return
		}
	}
	if err := sheet.addSubCategories(categoryColumn, subcategoryColumn, categories); err != nil {
		fmt.Printf("addSubCategories err %v\n", err)
		return
	}

	removeRowFn := func(txt string) bool {
		return slices.Contains(filterCategories, txt)
	}
	if count, err := sheet.removeRows(subcategoryColumn, removeRowFn); err != nil {
		fmt.Printf("removeRows err %v\n", err)
		return
	} else {
		fmt.Printf("Removed %d rows because of category filter %s\n", count, *filterCategoriesFlag)
	}
	if count, err := sheet.removeFn(sheet.removeIfFn); err != nil {
		fmt.Printf("removeFn err %v\n", err)
		return
	} else {
		fmt.Printf("Removed %d rows because of special function\n", count)
	}

	fmt.Printf("%d rows\n", len(sheet.rows))
	outFile := strings.TrimSuffix(*fnameFlag, ".csv") + ".out.csv"
	fmt.Printf("Exporting %s\n", outFile)
	if err := sheet.writeFile(outFile); err != nil {
		fmt.Printf("writeFile err %v\n", err)
		return
	}
}

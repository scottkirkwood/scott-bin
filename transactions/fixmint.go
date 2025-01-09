// fix-mint fixes the dates of mint transactions
// Also puts in the parent categories
// Removes the DEBIT/CREDIT types and just uses minus sign
package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"regexp"
	"slices"
	"strings"
)

// Sheet contains a spreadsheet
type Sheet struct {
	fname string
	rows  [][]string
}

var fname = flag.String("f", "/home/scottkirkwood/Downloads/transactions.csv", "Import mint filename")
var rxDate = regexp.MustCompile(`(\d+)/(\d+)/(\d+)`)

type Categories struct {
	db                    []string
	ParentCategories      map[string]bool
	SubCategoriesToParent map[string]string
}

var subCategories = []string{
	">Auto & Transport",
	"Auto Insurance",
	"Auto Payment",
	"Boat",
	"Gas & Fuel",
	"Parking",
	"Public Transportation",
	"Ride Share",
	"Service & Parts",
	">Bills & Utilities",
	"Home Phone",
	"Internet",
	"Mobile Phone",
	"Television",
	"Utilities",
	">Business Services",
	"Advertising",
	"Legal",
	"Office Supplies",
	"Printing",
	"Shipping",
	">Education",
	"Books & Supplies",
	"Student Loan",
	"Tuition",
	">Entertainment",
	"Amusement",
	"Arts",
	"Movies & DVDs",
	"Music",
	"Newspapers & Magazines",
	">Fees & Charges",
	"ATM Fee",
	"Bank Fee",
	"Finance Charge",
	"Late Fee",
	"Service Fee",
	"Trade Commissions",
	">Financial",
	"Financial Advisor",
	"Life Insurance",
	">Food & Dining",
	"Alcohol & Bars",
	"Coffee Shops",
	"Fast Food",
	"Food Delivery",
	"Groceries",
	"Restaurants",
	">Gifts & Donations",
	"Charity",
	"Flowers",
	"Gift",
	">Health & Fitness",
	"Dentist",
	"Doctor",
	"Eyecare",
	"Gym",
	"Health Insurance",
	"Pharmacy",
	"Sports",
	">Hide from Budgets & Trends",
	">Home",
	"Furnishings",
	"Home Improvement",
	"Home Insurance",
	"Home Services",
	"Home Supplies",
	"Lawn & Garden",
	"Mortgage & Rent",
	">Income",
	"Bonus",
	"Interest Income",
	"Paycheck",
	"Reimbursement",
	"Rental Income",
	"Returned Purchase",
	"cnpq",
	">Investments",
	"Buy",
	"Deposit",
	"Dividend & Cap Gains",
	"Sell",
	"Withdrawal",
	">Kids",
	"Allowance",
	"Baby Supplies",
	"Babysitter & Daycare",
	"Child Support",
	"Kids Activities",
	"Toys",
	">Loans",
	"Loan Fees and Charges",
	"Loan Insurance",
	"Loan Interest",
	"Loan Payment",
	"Loan Principal",
	">Misc Expenses",
	">Personal Care",
	"Hair",
	"Laundry",
	"Spa & Massage",
	">Pets",
	"Pet Food & Supplies",
	"Pet Grooming",
	"Veterinary",
	">Shopping",
	"Books",
	"Clothing",
	"Computer/Video Games",
	"Electronics & Software",
	"Hobbies",
	"Sporting Goods",
	">Taxes",
	"Federal Tax",
	"Local Tax",
	"Property Tax",
	"Sales Tax",
	"State Tax",
	">Transfer",
	"Credit Card Payment",
	"To GIC",
	"Transfer for Cash Spending",
	">Travel",
	"Air Travel",
	"Hotel",
	"Rental Car & Taxi",
	"Tourism",
	"Vacation",
	">Uncategorized",
	"Cash & ATM",
	"Check",
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

func fixUSDate(d string) string {
	grab := rxDate.FindAllStringSubmatch(d, 1)
	if len(grab) == 0 {
		return d // Don't change
	}
	// mm/dd/yyyy to yyyy-mm-dd
	mm, dd, yyyy := grab[0][1], grab[0][2], grab[0][3]
	if len(mm) == 1 {
		mm = "0" + mm
	}
	if len(dd) == 1 {
		dd = "0" + dd
	}
	return fmt.Sprintf("%s-%s-%s", yyyy, mm, dd)
}

// colIndex returns the 0 based index of the column or -1 if not found
func (s *Sheet) colIndex(colName string) int {
	return slices.Index(s.rows[0], colName)
}

// fixUSDateList changes a US date to ISO 8601 format in place
func (s *Sheet) fixUSDateList(colName string) error {
	col := s.colIndex(colName)
	for i, row := range s.rows {
		if i == 0 {
			continue
		}
		s.rows[i][col] = fixUSDate(row[col])
	}
	return nil
}

// addSubCategories makes `colName` the new `newColName` and inserts a column
// to the left which is the parent category
func (s *Sheet) addSubCategories(colName, newColName string, subCategories Categories) error {
	colNameIndex := s.colIndex(colName)
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

// removeTransactionTypeCol removes "Transaction Type" col an updates "Amount" col
// to the left which is the parent category
func (s *Sheet) removeTransactionTypeCol(colName string) error {
	colNameIndex := s.colIndex(colName)
	transTypeIndex := s.colIndex("Transaction Type")
	for i, row := range s.rows {
		if i > 0 {
			mult := 1
			if row[transTypeIndex] == "credit" {
				mult = -1
			} else if row[transTypeIndex] != "debit" {
				return fmt.Errorf("expecting debit, got %q", row[transTypeIndex])
			}
			if mult == -1 {
				s.rows[i][colNameIndex] = "-1" + s.rows[i][colNameIndex]
			}
		}
		s.rows[i] = slices.Delete(s.rows[i], transTypeIndex, transTypeIndex+1)
	}
	return nil
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
	fmt.Printf("Importing %s\n", *fname)
	sheet, err := importFile(*fname)
	if err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
	sheet.fixUSDateList("Date")
	categories := initCategories(subCategories)
	if err := sheet.addSubCategories("Category", "Subcategory", categories); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
	if err := sheet.removeTransactionTypeCol("Amount"); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}

	fmt.Printf("%d rows\n", len(sheet.rows))
	*fname = strings.TrimSuffix(*fname, ".csv") + ".out.csv"
	fmt.Printf("Exporting %s\n", *fname)
	if err := sheet.writeFile(*fname); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
}

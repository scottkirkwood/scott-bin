// fix-mint fixes the dates of mint transactions
package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"regexp"
)

var fname = flag.String("f", "/home/scottkirkwood/Downloads/transactions.csv", "Import mint filename")

var rxDate = regexp.MustCompile(`(\d+)/(\d+)/(\d+)`)

func importFile(fname string) ([][]string, error) {
	f, err := os.Open(fname)
	if err != nil {
		return nil, fmt.Errorf("unable to read input file "+fname, err)
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	return csvReader.ReadAll()
}

func writeFile(fname string, lines [][]string) error {
	f, err := os.Create(fname)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	w.WriteAll(lines)
	return nil
}

func fixUSDate(d string) string {
	grab := rxDate.FindAllStringSubmatch(d, 1)
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

// fixUSDateList changes a US date to ISO 8601 format in place
func fixUSDateList(rows [][]string, col int, headerRow bool) {
	for i, row := range rows {
		if i == 0 {
			continue
		}
		rows[i][col] = fixUSDate(row[col])
	}
}

func main() {
	fmt.Printf("Importing %s\n", *fname)
	rows, err := importFile(*fname)
	if err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
	fixUSDateList(rows, 0, true)
	fmt.Printf("%d rows\n", len(rows))
	*fname = *fname + ".out"
	if err := writeFile(*fname, rows); err != nil {
		fmt.Printf("err %v\n", err)
		return
	}
}
